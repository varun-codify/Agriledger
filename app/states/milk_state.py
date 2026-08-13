"""Milk & Society Bills state.

Records daily milk deliveries to societies (Aavin, Hatsun, etc.) from the
society's bill slip. Supports OCR scanning of the slip via Gemini vision so
the farmer spends seconds instead of minutes on data entry, plus a
configurable fat%-slab rate table per society and per-society analytics.
"""

import datetime
import logging
from collections import defaultdict
from typing import Literal

import reflex as rx

from app.config import config
from app.database import crud
from app.services.gemini_service import extract_json, retry_across_models
from app.states.auth_state import AuthState
from app.states.transaction_state import TransactionState

# Common milk societies (Tamil Nadu / South India). Farmers can also type a
# custom society name — it will be remembered automatically.
DEFAULT_SOCIETIES = [
    "Aavin",
    "Hatsun Agro",
    "Heritage",
    "Dodla",
    "Arokya",
    "Private Customer",
    "Other",
]

PaymentStatus = Literal["pending", "paid"]


class MilkState(rx.State):
    """Manages milk bill entry, OCR scanning, rate checking, and analytics."""

    # ── Bill entry form ─────────────────────────────────────────────────
    date: str = datetime.date.today().isoformat()
    society: str = "Aavin"
    liters: float = 0.0
    fat_percentage: float = 0.0
    snf_percentage: float = 0.0
    clr: float = 0.0
    rate_per_liter: float = 0.0
    amount: float = 0.0  # amount printed on the bill slip
    bill_number: str = ""
    payment_status: PaymentStatus = "pending"
    animal_id: str = ""
    notes: str = ""

    # ── OCR scan state ──────────────────────────────────────────────────
    scanning: bool = False
    scan_message: str = ""

    # ── Rate checker panel ──────────────────────────────────────────────
    rate_society: str = "Aavin"
    rate_slabs: list[dict] = []  # [{"fat_min": 3.0, "rate": 40.0}, ...]
    rate_saved: bool = False

    # ── UI state ────────────────────────────────────────────────────────
    pending_delete_id: str = ""

    # ── Field setters (defensive: strings → floats, never crash) ────────

    @rx.event
    def set_date(self, value: str):
        self.date = value

    @rx.event
    def set_society(self, value: str):
        self.society = value

    @rx.event
    def set_liters(self, value: str):
        self.liters = self._to_float(value, 0.0, 100000.0)

    @rx.event
    def set_fat_percentage(self, value: str):
        self.fat_percentage = self._to_float(value, 0.0, 10.0)

    @rx.event
    def set_snf_percentage(self, value: str):
        self.snf_percentage = self._to_float(value, 6.0, 12.0)

    @rx.event
    def set_clr(self, value: str):
        self.clr = self._to_float(value, 0.0, 40.0)

    @rx.event
    def set_rate_per_liter(self, value: str):
        self.rate_per_liter = self._to_float(value, 0.0, 10000.0)

    @rx.event
    def set_amount(self, value: str):
        self.amount = self._to_float(value, 0.0, 10000000.0)

    @rx.event
    def set_bill_number(self, value: str):
        self.bill_number = value[:60]

    @rx.event
    def set_payment_status(self, value: str):
        self.payment_status = value if value in ("pending", "paid") else "pending"

    @rx.event
    def set_animal_id(self, value: str):
        self.animal_id = value

    @rx.event
    def set_notes(self, value: str):
        self.notes = value

    @rx.event
    def set_pending_delete_id(self, value: str):
        self.pending_delete_id = value

    def _to_float(self, value, lo: float, hi: float) -> float:
        try:
            v = float(value or 0)
        except (TypeError, ValueError):
            v = 0.0
        return max(lo, min(hi, v))

    # ── Derived data ────────────────────────────────────────────────────

    @rx.var
    async def milk_sales(self) -> list[dict]:
        ts = await self.get_state(TransactionState)
        return sorted(
            ts.milk_sales, key=lambda s: s.get("date", ""), reverse=True
        )

    @rx.var
    async def societies(self) -> list[str]:
        ts = await self.get_state(TransactionState)
        custom = sorted(
            {s.get("buyer") for s in ts.milk_sales if s.get("buyer")}
            - set(DEFAULT_SOCIETIES)
        )
        return DEFAULT_SOCIETIES + custom

    @rx.var
    async def month_litres(self) -> float:
        sales = await self._month_sales()
        return round(sum(float(s.get("liters", 0)) for s in sales), 1)

    @rx.var
    async def month_income(self) -> float:
        sales = await self._month_sales()
        return round(sum(float(s.get("total_price", 0)) for s in sales), 2)

    @rx.var
    async def pending_amount(self) -> float:
        sales = await self._month_sales()
        return round(
            sum(
                float(s.get("total_price", 0))
                for s in sales
                if s.get("payment_status", "pending") != "paid"
            ),
            2,
        )

    @rx.var
    async def avg_fat_month(self) -> float:
        sales = await self._month_sales()
        values = [
            float(s.get("fat_percentage", 0))
            for s in sales
            if s.get("fat_percentage")
        ]
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)

    @rx.var
    async def avg_snf_month(self) -> float:
        sales = await self._month_sales()
        values = [
            float(s.get("snf_percentage", 0))
            for s in sales
            if s.get("snf_percentage")
        ]
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)

    async def _month_sales(self) -> list[dict]:
        """All milk sales from the current calendar month (plain helper)."""
        ts = await self.get_state(TransactionState)
        today = datetime.date.today()
        month_start = today.replace(day=1)
        return [
            s
            for s in ts.milk_sales
            if _parse_date(s.get("date", "")) >= month_start
        ]

    @rx.var
    async def society_stats(self) -> list[dict]:
        """Per-society month-to-date: litres, income, avg fat/SNF, pending."""
        ts = await self.get_state(TransactionState)
        today = datetime.date.today()
        month_start = today.replace(day=1)
        by_society: dict[str, dict] = defaultdict(
            lambda: {"litres": 0.0, "income": 0.0, "fat_sum": 0.0,
                     "snf_sum": 0.0, "bills": 0, "pending": 0.0}
        )
        for s in ts.milk_sales:
            if _parse_date(s.get("date", "")) < month_start:
                continue
            name = s.get("buyer") or "Other"
            row = by_society[name]
            row["litres"] += float(s.get("liters", 0))
            row["income"] += float(s.get("total_price", 0))
            if s.get("fat_percentage"):
                row["fat_sum"] += float(s["fat_percentage"])
            if s.get("snf_percentage"):
                row["snf_sum"] += float(s["snf_percentage"])
            row["bills"] += 1
            if s.get("payment_status", "pending") != "paid":
                row["pending"] += float(s.get("total_price", 0))
        result = []
        for name, row in by_society.items():
            bills = row["bills"]
            result.append(
                {
                    "society": name,
                    "litres": round(row["litres"], 1),
                    "income": round(row["income"], 2),
                    "avg_fat": round(row["fat_sum"] / bills, 2) if bills else 0.0,
                    "avg_snf": round(row["snf_sum"] / bills, 2) if bills else 0.0,
                    "bills": bills,
                    "pending": round(row["pending"], 2),
                }
            )
        result.sort(key=lambda r: r["income"], reverse=True)
        return result

    # ── Rate checker ────────────────────────────────────────────────────

    @rx.var
    async def suggested_rate(self) -> float:
        """Expected rate/L for the current fat% based on the society's slabs."""
        auth = await self.get_state(AuthState)
        table = await crud.get_milk_rate_table(auth.farm_id, self.society)
        if not table or not table.get("slabs"):
            return 0.0
        return _suggest_rate_for_fat(self.fat_percentage, table["slabs"])

    @rx.var
    def expected_amount(self) -> float:
        return round(self.liters * self.rate_per_liter, 2)

    @rx.var
    def amount_mismatch(self) -> bool:
        """True when the bill amount disagrees with litres × rate."""
        expected = self.expected_amount
        return (
            self.amount > 0
            and self.rate_per_liter > 0
            and abs(self.amount - expected) > max(1.0, expected * 0.02)
        )

    @rx.event
    async def use_suggested_rate(self):
        rate = await self.suggested_rate
        if rate <= 0:
            return rx.toast.error(
                "No rate table for this society. Add one in the Rate Checker panel."
            )
        self.rate_per_liter = rate
        if self.amount <= 0:
            self.amount = round(self.liters * rate, 2)
        return rx.toast.success(f"Applied suggested rate ₹{rate:g}/L.")

    @rx.event
    async def load_rate_table(self):
        auth = await self.get_state(AuthState)
        table = await crud.get_milk_rate_table(auth.farm_id, self.rate_society)
        self.rate_slabs = list(table.get("slabs", [])) if table else []
        self.rate_saved = False

    @rx.event
    def set_rate_society(self, value: str):
        self.rate_society = value
        self.rate_slabs = []
        self.rate_saved = False

    @rx.event
    def add_slab(self):
        self.rate_slabs.append({"fat_min": 3.0, "rate": 0.0})
        self.rate_saved = False

    @rx.event
    def remove_slab(self, index: int):
        if 0 <= index < len(self.rate_slabs):
            self.rate_slabs.pop(index)
            self.rate_saved = False

    @rx.event
    def set_slab_fat(self, index: int, value: str):
        if 0 <= index < len(self.rate_slabs):
            self.rate_slabs[index]["fat_min"] = self._to_float(value, 0.0, 20.0)
            self.rate_saved = False

    @rx.event
    def set_slab_rate(self, index: int, value: str):
        if 0 <= index < len(self.rate_slabs):
            self.rate_slabs[index]["rate"] = self._to_float(value, 0.0, 10000.0)
            self.rate_saved = False

    @rx.event
    async def save_rate_table(self):
        auth = await self.get_state(AuthState)
        valid = [
            s for s in self.rate_slabs if s["fat_min"] > 0 and s["rate"] >= 0
        ]
        valid.sort(key=lambda s: s["fat_min"])
        ok = await crud.upsert_milk_rate_table(
            auth.farm_id, self.rate_society, valid
        )
        if ok:
            self.rate_slabs = valid
            self.rate_saved = True
            return rx.toast.success(
                f"Rate table saved for {self.rate_society}."
            )
        return rx.toast.error("Could not save the rate table.")

    # ── Bill lifecycle ──────────────────────────────────────────────────

    @rx.event
    async def add_bill(self):
        """Save the society bill slip as a milk sale + income transaction."""
        if self.liters <= 0:
            return rx.toast.error("Litres must be greater than 0.")
        if not 0 <= self.fat_percentage <= 10:
            return rx.toast.error("Fat % must be between 0 and 10.")
        if not 6 <= self.snf_percentage <= 12:
            return rx.toast.error("SNF % must be between 6 and 12.")
        if self.rate_per_liter <= 0 and self.amount <= 0:
            return rx.toast.error(
                "Enter the rate per litre (or the total amount from the bill)."
            )
        if self.rate_per_liter <= 0 and self.liters > 0:
            self.rate_per_liter = round(self.amount / self.liters, 2)
        total_price = self.amount if self.amount > 0 else self.expected_amount

        ts = await self.get_state(TransactionState)
        auth = await self.get_state(AuthState)
        new_id = str(datetime.datetime.now().timestamp())
        new_sale = {
            "id": new_id,
            "date": self.date,
            "animal_id": self.animal_id or None,
            "liters": round(self.liters, 2),
            "fat_percentage": round(self.fat_percentage, 2),
            "snf_percentage": round(self.snf_percentage, 2),
            "clr": round(self.clr, 1) if self.clr else None,
            "water_ratio": None,
            "rate_per_liter": round(self.rate_per_liter, 2),
            "total_price": round(total_price, 2),
            "buyer": self.society or None,
            "bill_number": self.bill_number or None,
            "payment_status": self.payment_status,
            "paid_date": (
                self.date if self.payment_status == "paid" else None
            ),
            "notes": self.notes or None,
            "farm_id": auth.farm_id,
        }
        # Also record the income so reports & dashboard aggregates include it.
        new_tx = {
            "type": "income",
            "category": {"name": "Milk Sale", "icon": "droplets"},
            "amount": round(total_price, 2),
            "date": self.date,
            "notes": f"[{new_id}] Sold {round(self.liters, 1)}L milk to {self.society}",
            "farm_id": auth.farm_id,
        }
        sale_ok = await crud.create_milk_sale(new_sale)
        tx_ok = await crud.create_transaction(new_tx) if sale_ok else False
        if sale_ok:
            ts.milk_sales.append(new_sale)
            if tx_ok:
                ts.transactions.append(new_tx)
            else:
                logging.warning(
                    f"Milk sale {new_id} saved but income transaction failed."
                )
            self.reset_form()
            return rx.toast.success("Bill saved successfully!")
        return rx.toast.error("Could not save the bill. Please try again.")

    @rx.event
    def reset_form(self):
        today = datetime.date.today().isoformat()
        self.date = today
        self.liters = 0.0
        self.fat_percentage = 0.0
        self.snf_percentage = 0.0
        self.clr = 0.0
        self.rate_per_liter = 0.0
        self.amount = 0.0
        self.bill_number = ""
        self.animal_id = ""
        self.notes = ""
        self.scan_message = ""

    @rx.event
    async def toggle_payment(self, sale_id: str):
        ts = await self.get_state(TransactionState)
        for i, s in enumerate(ts.milk_sales):
            if s["id"] == sale_id:
                new_status = (
                    "pending"
                    if s.get("payment_status", "pending") == "paid"
                    else "paid"
                )
                updates = {
                    "payment_status": new_status,
                    "paid_date": (
                        datetime.date.today().isoformat()
                        if new_status == "paid"
                        else None
                    ),
                }
                if await crud.update_milk_sale(sale_id, updates):
                    ts.milk_sales[i] = {**s, **updates}
                    return rx.toast.success(
                        "Bill marked as paid. 🎉"
                        if new_status == "paid"
                        else "Bill marked as pending."
                    )
                return rx.toast.error("Could not update payment status.")
        return rx.toast.error("Bill not found.")

    @rx.event
    async def delete_bill(self, sale_id: str):
        ts = await self.get_state(TransactionState)
        auth = await self.get_state(AuthState)
        prefix = f"[{sale_id}]"
        # Remove the linked income transaction too (kept notes marker).
        await crud.delete_transactions_by_note(auth.farm_id, prefix)
        ts.transactions = [
            t
            for t in ts.transactions
            if not str(t.get("notes", "")).startswith(prefix)
        ]
        ts.milk_sales = [s for s in ts.milk_sales if s["id"] != sale_id]
        await crud.delete_milk_sale(sale_id)
        self.pending_delete_id = ""
        return rx.toast.success("Bill deleted.")

    # ── OCR scanning (Gemini vision) ────────────────────────────────────

    @rx.event
    async def handle_bill_upload(self, files: list[rx.UploadFile]):
        """Scan the uploaded bill slip and prefill the form."""
        if not files:
            return
        self.scanning = True
        self.scan_message = ""
        try:
            f = files[0]
            data = await f.read()
            mime = getattr(f, "content_type", None) or "image/jpeg"
            if not data or len(data) > 10_000_000:
                self.scanning = False
                self.scan_message = (
                    "Could not read the image (or it's over 10 MB). "
                    "Please upload the bill photo again."
                )
                return

            result = None
            if config.gemini.is_configured:
                try:
                    from google import genai
                    from google.genai import types

                    client = genai.Client(api_key=config.gemini.api_key)
                    prompt = (
                        "You are an OCR assistant for Indian dairy milk society "
                        "bill slips (Aavin, Hatsun Agro, etc.). Extract the fields "
                        "below from the image and reply with STRICT JSON containing "
                        "only these keys (use null when a value is not visible):\n"
                        '{"date": "YYYY-MM-DD", "society": "string", '
                        '"litres": number, "fat_percentage": number, '
                        '"snf_percentage": number, "clr": number, '
                        '"rate_per_liter": number, "total_amount": number, '
                        '"bill_number": "string"}\n'
                        "Rules: numbers without units or symbols (fat 4.2, snf 8.5, "
                        "litres 12.5); if only total amount and litres are present, "
                        "compute rate_per_liter = amount / litres; prefer the date "
                        "printed on the bill; ignore farmer/member ID numbers."
                    )

                    async def _run_ocr(model: str):
                        return await client.aio.models.generate_content(
                            model=model,
                            contents=[
                                prompt,
                                types.Part.from_bytes(data=data, mime_type=mime),
                            ],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json"
                            ),
                        )

                    response = await retry_across_models(_run_ocr)
                    if response:
                        result = extract_json(response.text)
                except Exception as e:
                    logging.exception(f"Milk bill OCR failed: {e}")
            if not result:
                self.scanning = False
                self.scan_message = (
                    "Could not read the bill automatically. Enter the details "
                    "manually below. To enable scanning, set GEMINI_API_KEY in the "
                    "project's .env file (Settings → Integrations shows the status) "
                    "and restart the app."
                )
                return
            self._apply_ocr_result(result)
            self.scanning = False
            self.scan_message = (
                "Bill scanned! Please check the fields and press Save Bill."
            )
            return rx.toast.success("Bill scanned ✓")
        except Exception as e:
            logging.exception(f"Milk bill OCR failed: {e}")
            self.scanning = False
            self.scan_message = "Scan failed. Please enter the details manually."

    def _apply_ocr_result(self, result: dict):
        """Fill the form from OCR output, sanitizing every value."""
        today = datetime.date.today()
        date = today.isoformat()
        raw_date = result.get("date")
        if raw_date:
            try:
                parsed = datetime.date.fromisoformat(str(raw_date))
                if today >= parsed >= today - datetime.timedelta(days=365):
                    date = parsed.isoformat()
            except ValueError:
                pass
        self.date = date

        society = str(result.get("society") or "").strip()
        if society:
            self.society = society[:50]

        self.liters = self._to_float(result.get("litres", 0), 0.0, 100000.0)
        self.fat_percentage = self._to_float(
            result.get("fat_percentage", 0), 0.0, 10.0
        )
        self.snf_percentage = self._to_float(
            result.get("snf_percentage", 0), 6.0, 12.0
        )
        self.clr = self._to_float(result.get("clr", 0), 0.0, 40.0)
        self.rate_per_liter = self._to_float(
            result.get("rate_per_liter", 0), 0.0, 10000.0
        )
        self.amount = self._to_float(result.get("total_amount", 0), 0.0, 10000000.0)
        self.bill_number = str(result.get("bill_number") or "").strip()[:60]


def _parse_date(value: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return datetime.date.min


def _suggest_rate_for_fat(fat: float, slabs: list[dict]) -> float:
    """Highest slab whose fat_min is <= fat; 0.0 when no slab matches."""
    best = 0.0
    for s in slabs:
        try:
            if fat >= float(s.get("fat_min", 0)):
                best = float(s.get("rate", 0))
        except (TypeError, ValueError):
            continue
    return round(best, 2)

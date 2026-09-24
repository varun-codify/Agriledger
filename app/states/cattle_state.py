import datetime
import logging
import uuid

import reflex as rx

from app.database import crud
from app.states.auth_state import AuthState
from app.database.models import Cattle, HealthNote, MilkProduction, VaccinationRecord


def _to_bool(value) -> bool:
    """Normalize a browser form value into a real bool.

    HTML checkboxes submit the literal string "on" when checked and omit the
    field entirely when unchecked; Reflex may also deliver True/False or "".
    Accept the common truthy spellings and treat everything else as False.
    """
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ("1", "true", "yes", "on", "checked")


def _normalize_iso_date(raw: str) -> str | None:
    """Normalize a date submitted by a browser into ISO (YYYY-MM-DD).

    <input type="date"> submits YYYY-MM-DD, but some browsers/locales and
    mobile keyboards deliver MM/DD/YYYY (or DD-MM-YYYY). Returns None when
    the value cannot be parsed so callers can show a friendly error.
    """
    value = (raw or "").strip()
    if not value:
        return None
    # Already ISO.
    try:
        return datetime.date.fromisoformat(value).isoformat()
    except ValueError:
        pass
    # MM/DD/YYYY or MM-DD-YYYY (en-US input.value locale).
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _as_int(value, default: int = 0) -> int:
    """Coerce a DB/legacy value to int without raising."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_float(value, default: float = 0.0) -> float:
    """Coerce a DB/legacy value to float without raising."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_cattle_row(row: dict) -> Cattle:
    """Fill defaults for every required Cattle key.

    Legacy/corrupt rows (missing image_url, string bools, locale-formatted
    dates, None list fields, string numbers) must never crash computed vars
    or components that index into the row directly.
    """
    weight_raw = row.get("weight")
    clean: dict = {
        "id": str(row.get("id", "")),
        "name": str(row.get("name", "")),
        "animal_type": str(row.get("animal_type", "cow")),
        "tag_number": str(row.get("tag_number", "")),
        "age": _as_int(row.get("age", 0)),
        "breed": str(row.get("breed", "")),
        "purchase_date": _normalize_iso_date(row.get("purchase_date", ""))
        or str(row.get("purchase_date", "")),
        "purchase_price": _as_float(row.get("purchase_price", 0.0)),
        "image_url": str(row.get("image_url", "") or ""),
        "health_status": str(row.get("health_status", "Healthy")),
        "milk_production": row.get("milk_production") or [],
        "vaccinations": row.get("vaccinations") or [],
        "health_notes": row.get("health_notes") or [],
        "feed_records": row.get("feed_records") or [],
        "is_juvenile": _to_bool(row.get("is_juvenile", False)),
        "parent_id": row.get("parent_id"),
        "mother_id": row.get("mother_id"),
        "weight": _as_float(weight_raw, 0.0)
        if weight_raw not in (None, "")
        else None,
        "is_active": _to_bool(row.get("is_active", True)),
    }
    if "farm_id" in row:
        clean["farm_id"] = row["farm_id"]
    return clean


# Demo rows seeded into a farm's collection on first load. Kept as a
# module-level constant (not a state var) so it is never serialized to the
# browser — state base vars are sent to every client on every page load.
DEMO_CATTLE_DATA: list[Cattle] = [
        {
            "id": "c1",
            "name": "Lakshmi",
            "animal_type": "cow",
            "tag_number": "A001",
            "age": 4,
            "breed": "Jersey",
            "purchase_date": "2023-03-15",
            "purchase_price": 1200.0,
            "image_url": "https://api.dicebear.com/9.x/notionists/svg?seed=Lakshmi",
            "health_status": "Healthy",
            "milk_production": [
                {
                    "date": (
                        datetime.date.today() - datetime.timedelta(days=i)
                    ).isoformat(),
                    "liters": 12.5 + (i % 3 - 1) * 0.5,
                    "notes": None,
                }
                for i in range(30)
            ],
            "vaccinations": [
                {
                    "date": "2023-10-01",
                    "vaccine_name": "FMD Vaccine",
                    "veterinarian": "Dr. Smith",
                    "next_due_date": "2024-10-01",
                    "notes": "Routine checkup",
                }
            ],
            "health_notes": [
                {
                    "date": "2023-09-15",
                    "note": "Slight limp observed, recovered in 2 days.",
                    "severity": "Attention Needed",
                }
            ],
            "is_juvenile": False,
            "parent_id": None,
            "mother_id": None,
            "weight": 550.0,
            "is_active": True,
            "farm_id": "demo-farm",
        },
        {
            "id": "c2",
            "name": "Ganga",
            "animal_type": "buffalo",
            "tag_number": "B002",
            "age": 5,
            "breed": "Murrah",
            "purchase_date": "2022-11-20",
            "purchase_price": 1500.0,
            "image_url": "https://api.dicebear.com/9.x/notionists/svg?seed=Ganga",
            "health_status": "Vaccinated",
            "milk_production": [
                {
                    "date": datetime.date.today().isoformat(),
                    "liters": 8.0,
                    "notes": None,
                }
            ],
            "vaccinations": [],
            "health_notes": [],
            "is_juvenile": False,
            "parent_id": None,
            "mother_id": None,
            "weight": 680.0,
            "is_active": True,
            "farm_id": "demo-farm",
        },
        {
            "id": "s1",
            "name": "Shaun",
            "animal_type": "sheep",
            "tag_number": "S001",
            "age": 3,
            "breed": "Dorper",
            "purchase_date": "2023-01-10",
            "purchase_price": 250.0,
            "image_url": "https://api.dicebear.com/9.x/notionists/svg?seed=Shaun",
            "health_status": "Healthy",
            "milk_production": [],
            "vaccinations": [],
            "health_notes": [],
            "is_juvenile": False,
            "parent_id": None,
            "mother_id": None,
            "weight": 80.0,
            "is_active": True,
            "farm_id": "demo-farm",
        },
        {
            "id": "s2",
            "name": "Lamby",
            "animal_type": "sheep",
            "tag_number": "S002",
            "age": 0,
            "breed": "Dorper",
            "purchase_date": datetime.date.today().isoformat(),
            "purchase_price": 100.0,
            "image_url": "https://api.dicebear.com/9.x/notionists/svg?seed=Lamby",
            "health_status": "Healthy",
            "milk_production": [],
            "vaccinations": [],
            "health_notes": [],
            "is_juvenile": True,
            "parent_id": None,
            "mother_id": "s1",
            "weight": 15.0,
            "is_active": True,
            "farm_id": "demo-farm",
        },
        {
            "id": "g1",
            "name": "Billy",
            "animal_type": "goat",
            "tag_number": "G001",
            "age": 2,
            "breed": "Boer",
            "purchase_date": "2023-05-01",
            "purchase_price": 200.0,
            "image_url": "https://api.dicebear.com/9.x/notionists/svg?seed=Billy",
            "health_status": "Healthy",
            "milk_production": [],
            "vaccinations": [],
            "health_notes": [],
            "is_juvenile": False,
            "parent_id": None,
            "mother_id": None,
            "weight": 70.0,
            "is_active": True,
            "farm_id": "demo-farm",
        },
        {
            "id": "p1",
            "name": "Cluck",
            "animal_type": "hen",
            "tag_number": "P001",
            "age": 1,
            "breed": "Leghorn",
            "purchase_date": "2023-08-01",
            "purchase_price": 20.0,
            "image_url": "https://api.dicebear.com/9.x/notionists/svg?seed=Cluck",
            "health_status": "Healthy",
            "milk_production": [],
            "vaccinations": [],
            "health_notes": [],
            "is_juvenile": False,
            "parent_id": None,
            "mother_id": None,
            "weight": 2.5,
            "is_active": True,
            "farm_id": "demo-farm",
        },
        {
            "id": "p2",
            "name": "Pecky",
            "animal_type": "chick",
            "tag_number": "P002",
            "age": 0,
            "breed": "Leghorn",
            "purchase_date": datetime.date.today().isoformat(),
            "purchase_price": 5.0,
            "image_url": "https://api.dicebear.com/9.x/notionists/svg?seed=Pecky",
            "health_status": "Healthy",
            "milk_production": [],
            "vaccinations": [],
            "health_notes": [],
            "is_juvenile": True,
            "parent_id": None,
            "mother_id": "p1",
            "weight": 0.2,
            "is_active": True,
            "farm_id": "demo-farm",
        },
    ]


class CattleState(rx.State):
    """Manages the state for the cattle management module."""

    cattle_list: list[Cattle] = []
    show_add_cattle_dialog: bool = False
    new_cattle_date: str = datetime.date.today().isoformat()
    show_milk_dialog: bool = False
    show_vaccination_dialog: bool = False
    show_health_note_dialog: bool = False
    profile_active_tab: str = "Overview"
    current_dialog_date: str = datetime.date.today().isoformat()
    profile_loading: bool = True
    current_cattle: Cattle | None = None
    animal_type_filter: str = "all"
    view_mode: str = "cards"  # "cards" | "table"
    add_cattle_error: str = ""
    dialog_error: str = ""
    is_adding: bool = False

    def _reset_form_fields(self):
        self.new_cattle_date = datetime.date.today().isoformat()

    @rx.event
    def toggle_add_cattle_dialog(self, open: bool):
        self.show_add_cattle_dialog = open
        if not open:
            self._reset_form_fields()
        self.add_cattle_error = ""

    @rx.event
    async def fetch_cattle_list(self):
        """Fetches cattle list from DB (seeds demo data per-farm if empty)."""
        auth = await self.get_state(AuthState)
        await crud.ensure_farm_seed("cattle", auth.farm_id, DEMO_CATTLE_DATA)
        rows = await crud.get_all_cattle(farm_id=auth.farm_id)
        # Normalize legacy/corrupt rows (string bools, locale dates, missing
        # keys like image_url) so state validation and computed vars never trip.
        self.cattle_list = [_normalize_cattle_row(row) for row in rows]

    @rx.event
    async def add_cattle(self, form_data: dict):
        """Adds a new cattle to the list."""
        if self.is_adding:
            return None
        self.is_adding = True
        try:
            # Validate each field with a clear message; never clear the form on error.
            name = str(form_data.get("name", "")).strip()
            tag_number = str(form_data.get("tag_number", "")).strip()
            animal_type = str(form_data.get("animal_type", "")).strip()
            breed = str(form_data.get("breed", "")).strip()
            age_raw = str(form_data.get("age", "")).strip()
            weight_raw = str(form_data.get("weight", "")).strip()
            price_raw = str(form_data.get("purchase_price", "")).strip()
            purchase_date = str(form_data.get("purchase_date", "")).strip()

            if not name:
                self.add_cattle_error = "Name is required."
                return
            if not tag_number:
                self.add_cattle_error = "Tag number is required."
                return
            if not animal_type:
                self.add_cattle_error = "Please select an animal type."
                return
            if not age_raw:
                self.add_cattle_error = "Age is mandatory."
                return
            if not purchase_date:
                self.add_cattle_error = "Purchase date is mandatory."
                return
            try:
                age = int(age_raw)
                if age < 0:
                    self.add_cattle_error = "Age cannot be negative."
                    return
            except ValueError:
                self.add_cattle_error = "Age must be a valid whole number."
                return

            weight = None
            if weight_raw:
                try:
                    weight = float(weight_raw)
                except ValueError:
                    self.add_cattle_error = "Weight must be a valid number."
                    return

            purchase_price = 0.0
            if price_raw:
                try:
                    purchase_price = float(price_raw)
                except ValueError:
                    self.add_cattle_error = "Purchase price must be a valid number."
                    return

            iso_purchase_date = _normalize_iso_date(purchase_date)
            if not iso_purchase_date:
                self.add_cattle_error = "Purchase date must be a valid date."
                return

            try:
                auth = await self.get_state(AuthState)
                new_cattle: Cattle = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "animal_type": animal_type,
                    "tag_number": tag_number,
                    "age": age,
                    "breed": breed,
                    "purchase_date": iso_purchase_date,
                    "purchase_price": purchase_price,
                    "image_url": f"https://api.dicebear.com/9.x/notionists/svg?seed={name}",
                    "health_status": "Healthy",
                    "milk_production": [],
                    "vaccinations": [],
                    "health_notes": [],
                    "feed_records": [],
                    "is_juvenile": _to_bool(form_data.get("is_juvenile", False)),
                    "parent_id": form_data.get("parent_id"),
                    "mother_id": form_data.get("mother_id"),
                    "weight": weight,
                    "is_active": True,
                    "farm_id": auth.farm_id,
                }
                success = await crud.create_cattle(new_cattle)
                if success:
                    self.cattle_list.append(new_cattle)
                    self.add_cattle_error = ""
                    self.toggle_add_cattle_dialog(False)
                    try:
                        from app.states.notification_state import NotificationState

                        notif = await self.get_state(NotificationState)
                        notif.add_notification(
                            {
                                "title": "Animal added",
                                "message": f"{new_cattle['name']} is now in your herd.",
                                "type": "success",
                                "timestamp": "",
                            }
                        )
                    except Exception:
                        pass
                    return rx.toast.success("Animal added successfully!")
                else:
                    self.add_cattle_error = "Failed to save animal to database. Please try again."
            except Exception as e:  # noqa: BLE001 - surface a friendly message, log details
                logging.exception(f"Error adding animal: {e}")
                self.add_cattle_error = "Something went wrong while saving. Please check your inputs."
        finally:
            self.is_adding = False

    @rx.var
    def total_cattle(self) -> int:
        return len(self.cattle_list)

    @rx.var
    def total_milk_today(self) -> float:
        total = 0.0
        today_str = datetime.date.today().isoformat()
        for cattle in self.cattle_list:
            for record in cattle["milk_production"]:
                if record["date"] == today_str:
                    total += record["liters"]
        return round(total, 1)

    @rx.var
    def cattle_requiring_attention(self) -> int:
        return sum(
            (
                1
                for c in self.cattle_list
                if c["health_status"] in ["Sick", "Under Treatment"]
            )
        )

    @rx.var
    def total_cows(self) -> int:
        return sum((1 for c in self.cattle_list if c["animal_type"] == "cow"))

    @rx.var
    def total_buffaloes(self) -> int:
        return sum((1 for c in self.cattle_list if c["animal_type"] == "buffalo"))

    @rx.var
    def total_sheep(self) -> int:
        return sum(
            (
                1
                for c in self.cattle_list
                if c["animal_type"] == "sheep" and (not c["is_juvenile"])
            )
        )

    @rx.var
    def total_lambs(self) -> int:
        return sum(
            (
                1
                for c in self.cattle_list
                if c["animal_type"] == "sheep" and c["is_juvenile"]
            )
        )

    @rx.var
    def total_goats(self) -> int:
        return sum(
            (
                1
                for c in self.cattle_list
                if c["animal_type"] == "goat" and (not c["is_juvenile"])
            )
        )

    @rx.var
    def total_kids(self) -> int:
        return sum(
            (
                1
                for c in self.cattle_list
                if c["animal_type"] == "goat" and c["is_juvenile"]
            )
        )

    @rx.var
    def total_poultry(self) -> int:
        return sum(
            (
                1
                for c in self.cattle_list
                if c["animal_type"] in ["hen", "cock", "chick"]
            )
        )

    @rx.var
    def total_chicks(self) -> int:
        return sum((1 for c in self.cattle_list if c["animal_type"] == "chick"))

    @rx.var
    def active_animals(self) -> list[Cattle]:
        return [c for c in self.cattle_list if c["is_active"]]

    @rx.var
    def cattle_profitability_data(self) -> list[dict]:
        """Pre-compute profitability for each animal."""
        result = []
        for c in self.cattle_list:
            total_milk = sum(r["liters"] for r in c.get("milk_production", []))
            estimated_revenue = total_milk * 5.0
            purchase_cost = c.get("purchase_price", 0)
            profit = estimated_revenue - purchase_cost
            result.append({
                "id": c.get("id", ""),
                "name": c.get("name", ""),
                "animal_type": c.get("animal_type", ""),
                "image_url": c.get("image_url", ""),
                "total_milk": f"{total_milk:.1f}",
                "revenue": f"₹{estimated_revenue:,.0f}",
                "cost": f"₹{purchase_cost:,.0f}",
                "profit": f"₹{profit:,.0f}",
                "profit_positive": profit >= 0,
            })
        return result

    @rx.event
    def set_animal_filter(self, filter: str):
        self.animal_type_filter = filter

    @rx.event
    def set_view_mode(self, mode: str):
        """Switch between the card grid and the AG Grid table view."""
        if mode in ("cards", "table"):
            self.view_mode = mode

    @rx.var
    def filtered_cattle(self) -> list[Cattle]:
        if self.animal_type_filter == "all":
            return self.cattle_list
        if self.animal_type_filter == "poultry":
            return [
                c
                for c in self.cattle_list
                if c["animal_type"] in ["hen", "cock", "chick"]
            ]
        return [
            c for c in self.cattle_list if c["animal_type"] == self.animal_type_filter
        ]

    @rx.var
    def breedable_females(self) -> list[Cattle]:
        return [
            c
            for c in self.cattle_list
            if c["animal_type"] in ["cow", "buffalo"] and (not c["is_juvenile"])
        ]

    @rx.event
    def load_cattle_profile(self):
        """Load cattle profile based on the ID from the URL."""
        self.profile_loading = True
        yield
        self.current_cattle = None
        cattle_id = self.router.page.params.get("id", "")
        found = False
        for c in self.cattle_list:
            if c["id"] == cattle_id:
                self.current_cattle = c
                found = True
                break
        if not found:
            logging.warning(f"Cattle with ID {cattle_id} not found.")
        self.profile_loading = False

    @rx.var
    def days_owned(self) -> int:
        if not self.current_cattle or not self.current_cattle.get("purchase_date"):
            return 0
        try:
            purchase_date = datetime.date.fromisoformat(
                self.current_cattle["purchase_date"]
            )
        except ValueError:
            return 0
        return (datetime.date.today() - purchase_date).days

    @rx.var
    def total_milk_produced(self) -> float:
        if not self.current_cattle:
            return 0.0
        return round(
            sum(
                (record["liters"] for record in self.current_cattle["milk_production"])
            ),
            1,
        )

    @rx.var
    def average_daily_milk(self) -> float:
        if not self.current_cattle or not self.current_cattle["milk_production"]:
            return 0.0
        return round(
            self.total_milk_produced / len(self.current_cattle["milk_production"]), 1
        )

    @rx.var
    def milk_production_last_30_days(self) -> list[dict]:
        if not self.current_cattle:
            return []
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        recent_production = []
        for record in self.current_cattle.get("milk_production", []) or []:
            iso = _normalize_iso_date(record.get("date", ""))
            if not iso:
                continue
            try:
                record_date = datetime.date.fromisoformat(iso)
            except ValueError:
                continue
            if record_date >= thirty_days_ago:
                recent_production.append({**record, "date": iso})
        recent_production.sort(key=lambda x: x["date"])
        return [
            {
                "date": datetime.date.fromisoformat(record["date"]).strftime("%b %d"),
                "liters": record["liters"],
            }
            for record in recent_production
        ]

    @rx.event
    def set_profile_tab(self, tab: str):
        self.profile_active_tab = tab

    @rx.event
    def toggle_milk_dialog(self, open: bool):
        self.show_milk_dialog = open
        self.current_dialog_date = datetime.date.today().isoformat()
        self.dialog_error = ""

    @rx.event
    def toggle_vaccination_dialog(self, open: bool):
        self.show_vaccination_dialog = open
        self.current_dialog_date = datetime.date.today().isoformat()
        self.dialog_error = ""

    @rx.event
    def toggle_health_note_dialog(self, open: bool):
        self.show_health_note_dialog = open
        self.current_dialog_date = datetime.date.today().isoformat()
        self.dialog_error = ""

    @rx.event
    async def add_milk_entry(self, form_data: dict):
        if not self.current_cattle:
            return rx.toast.error("No cattle selected.")
        liters_raw = str(form_data.get("liters", "")).strip()
        if not liters_raw:
            self.dialog_error = "Liters is mandatory."
            return
        try:
            liters = float(liters_raw)
            if liters <= 0:
                self.dialog_error = "Liters must be a positive number."
                return
        except ValueError:
            self.dialog_error = "Liters must be a valid number."
            return
        new_entry: MilkProduction = {
            "date": form_data["date"],
            "liters": liters,
            "notes": form_data.get("notes"),
        }
        self.current_cattle["milk_production"].insert(0, new_entry)
        await crud.update_cattle(
            self.current_cattle["id"],
            {"milk_production": self.current_cattle["milk_production"]},
        )
        for i, c in enumerate(self.cattle_list):
            if c["id"] == self.current_cattle["id"]:
                self.cattle_list[i] = self.current_cattle
                break
        self.dialog_error = ""
        self.toggle_milk_dialog(False)
        return rx.toast.success("Milk entry added!")

    @rx.event
    async def add_vaccination_record(self, form_data: dict):
        if not self.current_cattle:
            return rx.toast.error("No cattle selected.")
        if not str(form_data.get("vaccine_name", "")).strip():
            self.dialog_error = "Vaccine name is required."
            return
        new_record: VaccinationRecord = {
            "date": form_data["date"],
            "vaccine_name": form_data["vaccine_name"],
            "veterinarian": form_data.get("veterinarian", ""),
            "next_due_date": form_data.get("next_due_date"),
            "notes": form_data.get("notes"),
        }
        self.current_cattle["vaccinations"].insert(0, new_record)
        if self.current_cattle["health_status"] != "Sick":
            self.current_cattle["health_status"] = "Vaccinated"
        await crud.update_cattle(
            self.current_cattle["id"],
            {
                "vaccinations": self.current_cattle["vaccinations"],
                "health_status": self.current_cattle["health_status"],
            },
        )
        for i, c in enumerate(self.cattle_list):
            if c["id"] == self.current_cattle["id"]:
                self.cattle_list[i] = self.current_cattle
                break
        self.dialog_error = ""
        self.toggle_vaccination_dialog(False)
        return rx.toast.success("Vaccination record added!")

    @rx.event
    async def add_health_note(self, form_data: dict):
        if not self.current_cattle:
            return rx.toast.error("No cattle selected.")
        if not str(form_data.get("note", "")).strip():
            self.dialog_error = "Note is required."
            return
        new_note: HealthNote = {
            "date": form_data["date"],
            "note": form_data["note"],
            "severity": form_data.get("severity", "Normal"),
        }
        self.current_cattle["health_notes"].insert(0, new_note)
        await crud.update_cattle(
            self.current_cattle["id"],
            {"health_notes": self.current_cattle["health_notes"]},
        )
        for i, c in enumerate(self.cattle_list):
            if c["id"] == self.current_cattle["id"]:
                self.cattle_list[i] = self.current_cattle
                break
        self.dialog_error = ""
        self.toggle_health_note_dialog(False)
        return rx.toast.success("Health note added!")

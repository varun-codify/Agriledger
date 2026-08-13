import datetime
from typing import Literal

import reflex as rx

from app.database import crud
from app.states.auth_state import AuthState
from app.database.models import Category, CoconutSale, MilkSale, Transaction


class TransactionState(rx.State):
    """Manages the state for transaction entry and storage."""

    current_step: int = 1
    transaction_type: Literal["income", "expense"] | None = None
    selected_category: Category | None = None
    amount_str: str = "0"
    date: str = datetime.date.today().isoformat()
    notes: str = ""
    transactions: list[Transaction] = []
    coconut_sales: list[CoconutSale] = []
    milk_sales: list[MilkSale] = []
    coconut_count: int = 0
    price_per_coconut: float = 0.0
    liters: float = 0.0
    fat_percentage: float = 0.0
    snf_percentage: float = 0.0
    clr: float = 0.0
    water_ratio: float = 0.0
    rate_per_liter: float = 0.0
    animal_id: str = ""
    buyer: str = "Aavin"
    bill_number: str = ""
    payment_status: str = "pending"
    show_quick_add: bool = False
    active_table_tab: str = "all"  # "all" | "milk" | "coconut"
    expense_categories: list[Category] = [
        {"name": "Cattle Feed", "icon": "wheat"},
        {"name": "Medicine", "icon": "syringe"},
        {"name": "Vaccination", "icon": "shield-check"},
        {"name": "Purchase of Animal", "icon": "git-fork"},
        {"name": "Shed/Shelter", "icon": "home"},
        {"name": "Machinery", "icon": "tractor"},
        {"name": "Ploughing", "icon": "tractor"},
        {"name": "Fencing", "icon": "fence"},
        {"name": "Irrigation", "icon": "shower-head"},
        {"name": "Seeds", "icon": "sprout"},
        {"name": "Fertilizers", "icon": "package"},
        {"name": "Pesticides", "icon": "bug"},
        {"name": "Electricity", "icon": "zap"},
        {"name": "Transport", "icon": "truck"},
        {"name": "Labor Wages", "icon": "users"},
        {"name": "Miscellaneous", "icon": "ellipsis"},
    ]
    income_categories: list[Category] = [
        {"name": "Milk Sale", "icon": "droplets"},
        {"name": "Selling Sheep", "icon": "indian-rupee"},
        {"name": "Selling Cattle", "icon": "indian-rupee"},
        {"name": "Coconut Sales", "icon": "tree-palm"},
        {"name": "Other Income", "icon": "archive"},
    ]

    @rx.var
    def recent_transactions(self) -> list[Transaction]:
        """Last 5 transactions in reverse chronological order."""
        return self.transactions[-5:][::-1]

    @rx.var
    def transactions_grid_data(self) -> list[dict]:
        """Flatten transactions for AG Grid display."""
        return [
            {
                "date": tx["date"],
                "type": tx["type"],
                "category_name": tx["category"]["name"],
                "amount": tx["amount"],
                "notes": tx.get("notes", ""),
            }
            for tx in self.transactions
        ]

    @rx.var
    def amount(self) -> float:
        return float(self.amount_str) if self.amount_str else 0.0

    @rx.var
    def current_categories(self) -> list[Category]:
        return (
            self.income_categories
            if self.transaction_type == "income"
            else self.expense_categories
        )

    @rx.var
    def wizard_steps(self) -> list[str]:
        """Wizard progress labels; extra step for Coconut/Milk detail forms."""
        steps = ["Type", "Category", "Amount", "Date", "Notes", "Review"]
        if self.selected_category:
            if self.selected_category["name"] == "Coconut Sales":
                steps.append("Coconut Details")
            elif self.selected_category["name"] == "Milk Sale":
                steps.append("Milk Details")
        return steps

    @rx.var
    def coconut_total_amount(self) -> float:
        return self.coconut_count * self.price_per_coconut

    @rx.var
    def milk_total_price(self) -> float:
        return self.liters * self.rate_per_liter

    @rx.event
    def reset_wizard(self):
        self.current_step = 1
        self.transaction_type = None
        self.selected_category = None
        self.amount_str = "0"
        self.date = datetime.date.today().isoformat()
        self.notes = ""
        self.coconut_count = 0
        self.price_per_coconut = 0.0
        self.liters = 0.0
        self.fat_percentage = 0.0
        self.snf_percentage = 0.0
        self.clr = 0.0
        self.water_ratio = 0.0
        self.rate_per_liter = 0.0
        self.animal_id = None
        self.buyer = "Aavin"
        self.bill_number = ""
        self.payment_status = "pending"

    @rx.event
    def next_step(self):
        if self.current_step < 8:
            self.current_step += 1

    @rx.event
    def prev_step(self):
        # Coconut/Milk detail steps (7/8) go straight back to category selection.
        if self.current_step in (7, 8):
            self.current_step = 2
        elif self.current_step > 1:
            self.current_step -= 1

    @rx.event
    def go_to_step(self, step: int):
        if 1 <= step <= 8:
            self.current_step = step

    @rx.event
    def set_transaction_type(self, type: Literal["income", "expense"]):
        self.transaction_type = type
        self.next_step()

    @rx.event
    def set_category(self, category: Category):
        self.selected_category = category
        if category["name"] == "Coconut Sales":
            self.go_to_step(7)
        elif category["name"] == "Milk Sale":
            self.go_to_step(8)
        else:
            self.next_step()

    @rx.event
    def handle_keypad(self, key: str):
        if key == "del":
            self.amount_str = self.amount_str[:-1] if len(self.amount_str) > 1 else "0"
        elif key == ".":
            if "." not in self.amount_str:
                self.amount_str += "."
        elif self.amount_str == "0":
            self.amount_str = key
        else:
            self.amount_str += key

    @rx.event
    async def fetch_transactions(self):
        """Fetch all transactions from DB"""
        auth = await self.get_state(AuthState)
        self.transactions = await crud.get_all_transactions(farm_id=auth.farm_id)
        self.coconut_sales = await crud.get_all_coconut_sales(farm_id=auth.farm_id)
        self.milk_sales = await crud.get_all_milk_sales(farm_id=auth.farm_id)

    @rx.event
    def modify_amount(self, value: int):
        new_amount = self.amount + value
        self.amount_str = str(max(0, new_amount))

    @rx.event
    def set_date(self, date: str):
        self.date = date

    @rx.event
    def set_notes(self, notes: str):
        self.notes = notes

    # ── Field setters for Coconut/Milk sale detail steps ────────────────────

    @rx.event
    def set_coconut_count(self, value: str):
        try:
            self.coconut_count = max(0, round(float(value or 0)))
        except ValueError:
            self.coconut_count = 0

    @rx.event
    def set_price_per_coconut(self, value: str):
        try:
            self.price_per_coconut = max(0.0, float(value or 0))
        except ValueError:
            self.price_per_coconut = 0.0

    @rx.event
    def set_liters(self, value: str):
        try:
            self.liters = max(0.0, float(value or 0))
        except ValueError:
            self.liters = 0.0

    @rx.event
    def set_fat_percentage(self, value: str):
        try:
            self.fat_percentage = max(0.0, float(value or 0))
        except ValueError:
            self.fat_percentage = 0.0

    @rx.event
    def set_snf_percentage(self, value: str):
        try:
            self.snf_percentage = max(0.0, float(value or 0))
        except ValueError:
            self.snf_percentage = 0.0

    @rx.event
    def set_clr(self, value: str):
        try:
            self.clr = max(0.0, float(value or 0))
        except ValueError:
            self.clr = 0.0

    @rx.event
    def set_water_ratio(self, value: str):
        try:
            self.water_ratio = max(0.0, float(value or 0))
        except ValueError:
            self.water_ratio = 0.0

    @rx.event
    def set_rate_per_liter(self, value: str):
        try:
            self.rate_per_liter = max(0.0, float(value or 0))
        except ValueError:
            self.rate_per_liter = 0.0

    @rx.event
    def set_buyer(self, value: str):
        self.buyer = value

    @rx.event
    def set_bill_number(self, value: str):
        self.bill_number = value[:60]

    @rx.event
    def set_payment_status(self, value: str):
        self.payment_status = value if value in ("pending", "paid") else "pending"

    @rx.event
    def set_animal_id(self, value: str):
        self.animal_id = value

    # ── Quick-add uses dedicated events so the wizard step is never touched ──

    @rx.event
    def quick_add_set_type(self, type: Literal["income", "expense"]):
        self.transaction_type = type
        self.selected_category = None

    @rx.event
    def quick_add_set_category(self, category: Category):
        self.selected_category = category

    async def _create_and_add_transaction(self, amount: float, notes: str):
        transaction: Transaction = {
            "type": self.transaction_type,
            "category": self.selected_category,
            "amount": amount,
            "date": self.date,
            "notes": notes,
            "farm_id": (await self.get_state(AuthState)).farm_id,
        }
        success = await crud.create_transaction(transaction)
        if success:
            self.transactions.append(transaction)
        return success

    @rx.event
    async def submit_transaction(self):
        if not self.transaction_type or not self.selected_category:
            return rx.toast.error("Type and category are required.")
        category_name = self.selected_category["name"]
        if category_name == "Coconut Sales":
            if self.coconut_count <= 0 or self.price_per_coconut <= 0:
                return rx.toast.error("Coconut count and price must be positive.")
            total_amount = self.coconut_total_amount
            new_sale: CoconutSale = {
                "id": str(datetime.datetime.now().timestamp()),
                "date": self.date,
                "coconut_count": self.coconut_count,
                "price_per_coconut": self.price_per_coconut,
                "total_amount": total_amount,
                "buyer": self.buyer or None,
                "notes": self.notes or None,
                "farm_id": (await self.get_state(AuthState)).farm_id,
            }
            if await crud.create_coconut_sale(new_sale):
                self.coconut_sales.append(new_sale)
                await self._create_and_add_transaction(
                    total_amount, f"Sold {self.coconut_count} coconuts"
                )
        elif category_name == "Milk Sale":
            if self.liters <= 0 or self.rate_per_liter <= 0:
                return rx.toast.error("Liters and rate must be positive.")
            if not 0 <= self.fat_percentage <= 10:
                return rx.toast.error("Fat percentage must be between 0 and 10.")
            if not 6 <= self.snf_percentage <= 12:
                return rx.toast.error("SNF percentage must be between 6 and 12.")
            total_price = self.milk_total_price
            new_sale: MilkSale = {
                "id": str(datetime.datetime.now().timestamp()),
                "date": self.date,
                "animal_id": self.animal_id or None,
                "liters": self.liters,
                "fat_percentage": self.fat_percentage,
                "snf_percentage": self.snf_percentage,
                "clr": self.clr or None,
                "water_ratio": self.water_ratio or None,
                "rate_per_liter": self.rate_per_liter,
                "total_price": total_price,
                "buyer": self.buyer or None,
                "bill_number": self.bill_number or None,
                "payment_status": self.payment_status,
                "paid_date": (
                    self.date if self.payment_status == "paid" else None
                ),
                "notes": self.notes or None,
                "farm_id": (await self.get_state(AuthState)).farm_id,
            }
            if await crud.create_milk_sale(new_sale):
                self.milk_sales.append(new_sale)
                await self._create_and_add_transaction(
                    total_price, f"Sold {self.liters}L of milk"
                )
        else:
            if self.amount <= 0:
                return rx.toast.error("Amount must be positive.")
            await self._create_and_add_transaction(self.amount, self.notes)
        self.reset_wizard()
        return rx.toast.success("Transaction added successfully!")

    @rx.event
    def set_active_table_tab(self, tab: str):
        """Switch between the transaction grids on the Transactions page."""
        if tab in ("all", "milk", "coconut"):
            self.active_table_tab = tab

    @rx.event
    def toggle_quick_add(self, open: bool | None = None):
        if open is not None:
            self.show_quick_add = open
        else:
            self.show_quick_add = not self.show_quick_add
        if not self.show_quick_add:
            self.reset_quick_add_form()

    @rx.event
    def reset_quick_add_form(self):
        self.transaction_type = None
        self.selected_category = None
        self.amount_str = "0"

    @rx.event
    async def quick_add_transaction(self):
        if self.transaction_type and self.selected_category and (self.amount > 0):
            transaction: Transaction = {
                "type": self.transaction_type,
                "category": self.selected_category,
                "amount": self.amount,
                "date": datetime.date.today().isoformat(),
                "notes": "Quick Add",
                "farm_id": (await self.get_state(AuthState)).farm_id,
            }
            success = await crud.create_transaction(transaction)
            if success:
                self.transactions.append(transaction)
                self.toggle_quick_add(False)
                return rx.toast.success("Quick transaction added!")
            else:
                return rx.toast.error("Failed to save transaction.")
        else:
            return rx.toast.error("Type, category, and amount are required.")

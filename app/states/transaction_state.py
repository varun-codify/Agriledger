import reflex as rx
from typing import TypedDict, Literal
import datetime
from app.database import crud
from app.database.models import Transaction, Category, CoconutSale, MilkSale


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
    water_ratio: float = 0.0
    rate_per_liter: float = 0.0
    animal_id: str | None = None
    buyer: str = ""
    show_quick_add: bool = False
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
        {"name": "Selling Sheep", "icon": "dollar-sign"},
        {"name": "Selling Cattle", "icon": "dollar-sign"},
        {"name": "Coconut Sales", "icon": "palm-tree"},
        {"name": "Other Income", "icon": "archive"},
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
        self.water_ratio = 0.0
        self.rate_per_liter = 0.0
        self.animal_id = None
        self.buyer = ""

    @rx.event
    def next_step(self):
        if self.current_step < 6:
            self.current_step += 1

    @rx.event
    def prev_step(self):
        if self.current_step > 1:
            self.current_step -= 1

    @rx.event
    def go_to_step(self, step: int):
        if 1 <= step <= 6:
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
        self.transactions = await crud.get_all_transactions()
        self.coconut_sales = await crud.get_all_coconut_sales()
        self.milk_sales = await crud.get_all_milk_sales()

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

    async def _create_and_add_transaction(self, amount: float, notes: str):
        transaction: Transaction = {
            "type": self.transaction_type,
            "category": self.selected_category,
            "amount": amount,
            "date": self.date,
            "notes": notes,
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
                "animal_id": self.animal_id,
                "liters": self.liters,
                "fat_percentage": self.fat_percentage,
                "snf_percentage": self.snf_percentage,
                "water_ratio": self.water_ratio or None,
                "rate_per_liter": self.rate_per_liter,
                "total_price": total_price,
                "buyer": self.buyer or None,
                "notes": self.notes or None,
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
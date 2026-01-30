import reflex as rx
from typing import TypedDict, Literal
import datetime
import uuid
import logging
from collections import defaultdict
from app.database import crud
from app.database.models import Cattle, MilkProduction, VaccinationRecord, HealthNote


class CattleState(rx.State):
    """Manages the state for the cattle management module."""

    cattle_list: list[Cattle] = []
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
        },
    ]
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

    def _reset_form_fields(self):
        self.new_cattle_date = datetime.date.today().isoformat()

    @rx.event
    def toggle_add_cattle_dialog(self, open: bool):
        self.show_add_cattle_dialog = open
        if not open:
            self._reset_form_fields()

    @rx.event
    async def fetch_cattle_list(self):
        """Fetches cattle list from DB."""
        crud.init_database_seeds({"cattle": self.DEMO_CATTLE_DATA})
        self.cattle_list = await crud.get_all_cattle()

    @rx.event
    async def add_cattle(self, form_data: dict):
        """Adds a new cattle to the list."""
        try:
            new_cattle: Cattle = {
                "id": str(uuid.uuid4()),
                "name": form_data["name"],
                "animal_type": form_data["animal_type"],
                "tag_number": form_data["tag_number"],
                "age": int(form_data["age"]),
                "breed": form_data["breed"],
                "purchase_date": form_data["purchase_date"],
                "purchase_price": float(form_data["purchase_price"]),
                "image_url": f"https://api.dicebear.com/9.x/notionists/svg?seed={form_data['name']}",
                "health_status": "Healthy",
                "milk_production": [],
                "vaccinations": [],
                "health_notes": [],
                "is_juvenile": form_data.get("is_juvenile", False),
                "parent_id": form_data.get("parent_id"),
                "mother_id": form_data.get("mother_id"),
                "weight": float(form_data.get("weight"))
                if form_data.get("weight")
                else None,
                "is_active": True,
            }
            success = await crud.create_cattle(new_cattle)
            if success:
                self.cattle_list.append(new_cattle)
                self.toggle_add_cattle_dialog(False)
                return rx.toast.success("Animal added successfully!")
            else:
                return rx.toast.error("Failed to save animal to database.")
        except (ValueError, KeyError) as e:
            logging.exception(f"Error adding animal: {e}")
            return rx.toast.error(f"Invalid data: Please check all fields. {e}")

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

    @rx.event
    def set_animal_filter(self, filter: str):
        self.animal_type_filter = filter

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
        if not self.current_cattle:
            return 0
        purchase_date = datetime.date.fromisoformat(
            self.current_cattle["purchase_date"]
        )
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
        recent_production = [
            record
            for record in self.current_cattle["milk_production"]
            if datetime.date.fromisoformat(record["date"]) >= thirty_days_ago
        ]
        recent_production.sort(key=lambda x: x["date"])
        return [
            {
                "date": datetime.datetime.fromisoformat(record["date"]).strftime(
                    "%b %d"
                ),
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

    @rx.event
    def toggle_vaccination_dialog(self, open: bool):
        self.show_vaccination_dialog = open
        self.current_dialog_date = datetime.date.today().isoformat()

    @rx.event
    def toggle_health_note_dialog(self, open: bool):
        self.show_health_note_dialog = open
        self.current_dialog_date = datetime.date.today().isoformat()

    @rx.event
    async def add_milk_entry(self, form_data: dict):
        if not self.current_cattle:
            return rx.toast.error("No cattle selected.")
        try:
            liters = float(form_data["liters"])
            if liters <= 0:
                return rx.toast.error("Liters must be a positive number.")
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
            self.toggle_milk_dialog(False)
            return rx.toast.success("Milk entry added!")
        except ValueError as e:
            logging.exception(f"Error adding milk entry: {e}")
            return rx.toast.error("Invalid input for liters.")

    @rx.event
    async def add_vaccination_record(self, form_data: dict):
        if not self.current_cattle:
            return rx.toast.error("No cattle selected.")
        if not form_data.get("vaccine_name"):
            return rx.toast.error("Vaccine name is required.")
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
        self.toggle_vaccination_dialog(False)
        return rx.toast.success("Vaccination record added!")

    @rx.event
    async def add_health_note(self, form_data: dict):
        if not self.current_cattle:
            return rx.toast.error("No cattle selected.")
        if not form_data.get("note"):
            return rx.toast.error("Note is required.")
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
        self.toggle_health_note_dialog(False)
        return rx.toast.success("Health note added!")
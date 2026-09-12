import datetime
import uuid

import reflex as rx

from app.database import crud
from app.database.models import (
    BreedingCycle,
    CalvingOutcome,
)
from app.states.auth_state import AuthState
from app.states.cattle_state import CattleState


def _normalize_iso_date(raw: str) -> str | None:
    """Normalize a date submitted by a browser into ISO (YYYY-MM-DD)."""
    value = (raw or "").strip()
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(value).isoformat()
    except ValueError:
        pass
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


# Demo rows seeded into a farm's collection on first load. Kept as a
# module-level constant (not a state var) so it is never serialized to the
# browser — state base vars are sent to every client on every page load.
DEMO_BREEDING_DATA: list[BreedingCycle] = [
    {
        "id": "bc1",
        "cattle_id": "c1",
        "cattle_name": "Lakshmi",
        "cattle_type": "cow",
        "hormone_injection_date": (
            datetime.date.today() - datetime.timedelta(days=40)
        ).isoformat(),
        "insemination_date": (
            datetime.date.today() - datetime.timedelta(days=35)
        ).isoformat(),
        "pregnancy_confirmed": False,
        "pregnancy_confirmation_date": None,
        "expected_calving_date": (
            datetime.date.today() + datetime.timedelta(days=245)
        ).isoformat(),
        "follow_up_checks": [],
        "repeat_breeding_indicator": False,
        "calf_born": False,
        "calf_sex": None,
        "calf_health": None,
        "birth_outcome": None,
        "notes": "First cycle for this year.",
        "status": "pending_confirmation",
        "created_date": (
            datetime.date.today() - datetime.timedelta(days=40)
        ).isoformat(),
    },
    {
        "id": "bc2",
        "cattle_id": "c2",
        "cattle_name": "Ganga",
        "cattle_type": "buffalo",
        "hormone_injection_date": (
            datetime.date.today() - datetime.timedelta(days=120)
        ).isoformat(),
        "insemination_date": (
            datetime.date.today() - datetime.timedelta(days=110)
        ).isoformat(),
        "pregnancy_confirmed": True,
        "pregnancy_confirmation_date": (
            datetime.date.today() - datetime.timedelta(days=80)
        ).isoformat(),
        "expected_calving_date": (
            datetime.date.today() + datetime.timedelta(days=200)
        ).isoformat(),
        "follow_up_checks": [
            {"date": "2024-05-01", "notes": "Ultrasound check normal."}
        ],
        "repeat_breeding_indicator": False,
        "calf_born": False,
        "calf_sex": None,
        "calf_health": None,
        "birth_outcome": None,
        "notes": "Second pregnancy.",
        "status": "pregnant",
        "created_date": (
            datetime.date.today() - datetime.timedelta(days=120)
        ).isoformat(),
    },
]


class BreedingState(rx.State):
    """Manages the state for breeding cycles."""

    breeding_cycles: list[BreedingCycle] = []
    show_add_breeding_dialog: bool = False
    show_pregnancy_confirmation_dialog: bool = False
    show_calving_record_dialog: bool = False
    pregnancy_confirmation_outcome: str = "pregnant"
    pregnancy_confirmation_date: str = datetime.date.today().isoformat()
    current_breeding_cycle: BreedingCycle | None = None
    selected_filter: str = "all"
    view_mode: str = "cards"  # "cards" | "table"
    new_breeding_cattle_id: str = ""
    new_hormone_date: str = datetime.date.today().isoformat()
    new_insemination_date: str = datetime.date.today().isoformat()
    add_breeding_error: str = ""
    calving_error: str = ""
    show_follow_up_dialog: bool = False
    follow_up_date: str = datetime.date.today().isoformat()
    follow_up_notes: str = ""

    @rx.event
    def toggle_follow_up_dialog(self, open: bool):
        self.show_follow_up_dialog = open
        if open:
            self.follow_up_date = datetime.date.today().isoformat()
            self.follow_up_notes = ""

    @rx.event
    def set_follow_up_date(self, value: str):
        self.follow_up_date = value

    @rx.event
    def set_follow_up_notes(self, value: str):
        self.follow_up_notes = value

    @rx.event
    async def submit_follow_up_check(self):
        """Persist a follow-up check for the cycle on the detail page."""
        notes = self.follow_up_notes.strip()
        if not notes:
            return rx.toast.error("Please add a note for the follow-up check.")
        if not self.current_breeding_cycle:
            return rx.toast.error("No breeding cycle selected.")
        cycle_id = self.current_breeding_cycle["id"]
        cycle = next((c for c in self.breeding_cycles if c["id"] == cycle_id), None)
        if cycle is None:
            return rx.toast.error("Could not find this breeding cycle.")
        normalized = _normalize_iso_date(self.follow_up_date)
        if not normalized:
            return rx.toast.error("Enter a valid date.")
        cycle["follow_up_checks"].append({"date": normalized, "notes": notes})
        await crud.update_breeding_cycle(
            cycle_id, {"follow_up_checks": cycle["follow_up_checks"]}
        )
        self.show_follow_up_dialog = False
        self.follow_up_notes = ""
        return rx.toast.info("Follow-up check added.")

    @rx.event
    def toggle_calving_record_dialog(self, open: bool):
        self.show_calving_record_dialog = open
        if open:
            self.calving_error = ""

    @rx.event
    def set_show_pregnancy_confirmation_dialog(self, open: bool):
        self.show_pregnancy_confirmation_dialog = open
        if open:
            self.pregnancy_confirmation_date = datetime.date.today().isoformat()

    @rx.event
    def set_pregnancy_confirmation_outcome(self, outcome: str):
        self.pregnancy_confirmation_outcome = outcome

    @rx.event
    def set_pregnancy_confirmation_date(self, date: str):
        self.pregnancy_confirmation_date = date

    @rx.var
    def pregnancy_check_due_date_str(self) -> str:
        if self.current_breeding_cycle:
            insemination_date = datetime.date.fromisoformat(
                self.current_breeding_cycle["insemination_date"]
            )
            return (insemination_date + datetime.timedelta(days=30)).isoformat()
        return ""

    @rx.var
    def filtered_breeding_cycles(self) -> list[BreedingCycle]:
        """Filters breeding cycles based on the selected status."""
        if self.selected_filter == "all":
            return self.breeding_cycles
        return [
            cycle
            for cycle in self.breeding_cycles
            if cycle["status"] == self.selected_filter
        ]

    @rx.var
    def pregnancy_checks_due(self) -> list[BreedingCycle]:
        """Cycles where pregnancy is not confirmed and 30+ days since insemination."""
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        result = []
        for cycle in self.breeding_cycles:
            if cycle.get("pregnancy_confirmed"):
                continue
            iso = _normalize_iso_date(cycle.get("insemination_date", ""))
            if not iso:
                continue
            try:
                if datetime.date.fromisoformat(iso) <= thirty_days_ago:
                    result.append(cycle)
            except ValueError:
                continue
        return result

    @rx.var
    def calvings_due_soon(self) -> list[BreedingCycle]:
        """Pregnant cycles with expected calving date within 7 days."""
        next_week = datetime.date.today() + datetime.timedelta(days=7)
        result = []
        for cycle in self.breeding_cycles:
            if cycle.get("status") != "pregnant":
                continue
            iso = _normalize_iso_date(cycle.get("expected_calving_date", ""))
            if not iso:
                continue
            try:
                if datetime.date.fromisoformat(iso) <= next_week:
                    result.append(cycle)
            except ValueError:
                continue
        return result

    @rx.event
    async def fetch_breeding_cycles(self):
        """Fetch cycles from DB (seeds demo data per-farm if empty)."""
        auth = await self.get_state(AuthState)
        await crud.ensure_farm_seed(
            "breeding_cycles", auth.farm_id, DEMO_BREEDING_DATA
        )
        self.breeding_cycles = await crud.get_all_breeding_cycles(farm_id=auth.farm_id)

    @rx.event
    def toggle_add_breeding_dialog(self, open: bool):
        self.show_add_breeding_dialog = open
        if open:
            self.add_breeding_error = ""

    @rx.event
    async def add_breeding_cycle(self, form_data: dict):
        """Adds a new breeding cycle."""
        cattle_id = form_data.get("cattle_id")
        if not cattle_id:
            self.add_breeding_error = "Please select an animal."
            return
        cattle_state = await self.get_state(CattleState)
        selected_cattle = next(
            (c for c in cattle_state.cattle_list if c["id"] == cattle_id), None
        )
        if not selected_cattle:
            self.add_breeding_error = "Selected animal not found."
            return
        insemination_date_str = str(form_data.get("insemination_date", "")).strip()
        hormone_date_str = str(form_data.get("hormone_injection_date", "")).strip()
        if not insemination_date_str:
            self.add_breeding_error = "Insemination date is mandatory."
            return
        if not hormone_date_str:
            self.add_breeding_error = "Hormone injection date is mandatory."
            return
        iso_insemination = _normalize_iso_date(insemination_date_str)
        if not iso_insemination:
            self.add_breeding_error = "Insemination date is invalid."
            return
        iso_hormone = _normalize_iso_date(hormone_date_str)
        if not iso_hormone:
            self.add_breeding_error = "Hormone injection date is invalid."
            return
        insemination_date = datetime.date.fromisoformat(iso_insemination)
        gestation_days = 310 if selected_cattle["animal_type"] == "buffalo" else 280
        expected_calving_date = insemination_date + datetime.timedelta(
            days=gestation_days
        )
        new_cycle: BreedingCycle = {
            "id": str(uuid.uuid4()),
            "cattle_id": selected_cattle["id"],
            "cattle_name": selected_cattle["name"],
            "cattle_type": selected_cattle["animal_type"],
            "hormone_injection_date": iso_hormone,
            "insemination_date": iso_insemination,
            "expected_calving_date": expected_calving_date.isoformat(),
            "notes": form_data.get("notes"),
            "status": "pending_confirmation",
            "pregnancy_confirmed": False,
            "pregnancy_confirmation_date": None,
            "follow_up_checks": [],
            "repeat_breeding_indicator": False,
            "calf_born": False,
            "calf_sex": None,
            "calf_health": None,
            "birth_outcome": None,
            "created_date": datetime.date.today().isoformat(),
            "farm_id": (await self.get_state(AuthState)).farm_id,
        }
        success = await crud.create_breeding_cycle(new_cycle)
        if success:
            self.breeding_cycles.append(new_cycle)
            self.add_breeding_error = ""
            self.show_add_breeding_dialog = False
            return rx.toast.success("Breeding cycle started successfully!")
        self.add_breeding_error = "Failed to start breeding cycle. Please try again."

    @rx.event
    async def update_pregnancy_status(
        self, cycle_id: str, confirmed: bool, confirmation_date: str
    ):
        status = "pregnant" if confirmed else "not_pregnant"
        updates = {
            "pregnancy_confirmed": confirmed,
            "pregnancy_confirmation_date": confirmation_date,
            "status": status,
        }
        await crud.update_breeding_cycle(cycle_id, updates)
        for i, cycle in enumerate(self.breeding_cycles):
            if cycle["id"] == cycle_id:
                self.breeding_cycles[i].update(updates)
                break
        self.show_pregnancy_confirmation_dialog = False
        return rx.toast.info("Pregnancy status updated.")

    @rx.event
    async def record_calving(self, cycle_id: str, form_data: dict):
        birth_outcome = str(form_data.get("birth_outcome", "")).strip()
        if not birth_outcome:
            self.calving_error = "Please select a birth outcome."
            return
        updates = {
            "calf_born": True,
            "calf_sex": form_data.get("calf_sex"),
            "calf_health": form_data.get("calf_health"),
            "birth_outcome": form_data.get("birth_outcome"),
            "status": "calved",
            "notes": form_data.get("notes"),
        }
        await crud.update_breeding_cycle(cycle_id, updates)
        for i, cycle in enumerate(self.breeding_cycles):
            if cycle["id"] == cycle_id:
                self.breeding_cycles[i].update(updates)
                break
        if (
            self.current_breeding_cycle
            and self.current_breeding_cycle["id"] == cycle_id
        ):
            self.current_breeding_cycle.update(updates)
        self.calving_error = ""
        self.show_calving_record_dialog = False
        return rx.toast.success("Calving recorded successfully!")

    @rx.event
    async def add_follow_up_check(self, cycle_id: str, check_date: str, notes: str):
        cycle = next((c for c in self.breeding_cycles if c["id"] == cycle_id), None)
        if cycle:
            cycle["follow_up_checks"].append({"date": check_date, "notes": notes})
            await crud.update_breeding_cycle(
                cycle_id, {"follow_up_checks": cycle["follow_up_checks"]}
            )
        return rx.toast.info("Follow-up check added.")

    @rx.event
    def set_filter(self, filter_value: str):
        self.selected_filter = filter_value

    @rx.event
    def set_view_mode(self, mode: str):
        """Switch between the card grid and the AG Grid table view."""
        if mode in ("cards", "table"):
            self.view_mode = mode

    @rx.event
    def load_breeding_detail(self, **kwargs):
        """Load breeding detail based on the ID from the URL."""
        cycle_id = self.router.page.params.get("id")
        if cycle_id:
            self.current_breeding_cycle = next(
                (c for c in self.breeding_cycles if c["id"] == cycle_id), None
            )


class CalvingRecordDialogState(rx.State):
    birth_outcome: CalvingOutcome = "live_birth"
    outcome_options: list[tuple[str, str]] = [
        ("live_birth", "Live Birth"),
        ("stillbirth", "Stillbirth"),
        ("aborted", "Aborted"),
    ]

    @rx.event
    def set_birth_outcome(self, outcome: CalvingOutcome):
        self.birth_outcome = outcome

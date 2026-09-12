"""Feed Intelligence & Nutrition Management.

Helps farmers optimize milk production and reduce feed costs. Integrates
with cattle milk production (CattleState), feed expenses (TransactionState)
and home-grown crops (CropState). All intelligence is rule-based and works
fully offline.
"""

import datetime
import logging
from collections import defaultdict

import reflex as rx

from app.database import crud
from app.database.models import (
    FeedConsumption,
    FeedingPlan,
    FeedStock,
    FeedType,
)
from app.states.auth_state import AuthState
from app.states.breeding_state import BreedingState
from app.states.cattle_state import CattleState
from app.states.crop_state import CropState
from app.states.transaction_state import TransactionState

DEFAULT_FEED_TYPES: list[dict] = [
    {"name": "Rice Bran", "category": "Concentrate", "unit": "kg", "cost_per_unit": 28.0, "is_custom": False},
    {"name": "Pelleted Feed (Theevanam)", "category": "Concentrate", "unit": "kg", "cost_per_unit": 35.0, "is_custom": False},
    {"name": "Cotton Seeds", "category": "Concentrate", "unit": "kg", "cost_per_unit": 40.0, "is_custom": False},
    {"name": "Groundnut Oil Cake", "category": "Concentrate", "unit": "kg", "cost_per_unit": 52.0, "is_custom": False},
    {"name": "Cholam (Fresh Green Fodder)", "category": "Home Grown", "unit": "bundles", "cost_per_unit": 15.0, "is_custom": False},
    {"name": "Cholam Dry Fodder", "category": "Home Grown", "unit": "bundles", "cost_per_unit": 20.0, "is_custom": False},
    {"name": "Rice Straw", "category": "Home Grown", "unit": "bundles", "cost_per_unit": 25.0, "is_custom": False},
]

PLAN_CATEGORIES = ["Calf", "Heifer", "Pregnant Cow", "Lactating Cow", "Dry Cow", "Bull"]

# Milk-price used to convert milk liters into ₹ for efficiency metrics.
MILK_PRICE_PER_LITER = 40.0

# Crop names that produce home-grown feed (fodder crops) for the crops→stock link.
FODDER_KEYWORDS = [
    "cholam", "sorghum", "jowar", "fodder", "grass", "straw", "hay",
    "silage", "maize", "corn", "ragi", "bajra", "millet", "cowpea",
    "horse gram", "napier", "guinea grass",
]

# Harvest units that map directly onto feed stock units.
FEED_UNITS = ("kg", "bundles", "bags")

# Daily nutrient requirements (arbitrary units) per animal group for the
# cheapest-ration optimizer. Treat as guidance; calibrate with a vet.
RATION_REQUIREMENTS = {
    "Calf": 4.0,
    "Heifer": 6.0,
    "Pregnant Cow": 8.0,
    "Lactating Cow": 12.0,
    "Dry Cow": 7.0,
    "Bull": 8.0,
}

# Rough nutrient density per kg by feed-name keyword (1.0 = richest).
NUTRIENT_SCORES = {
    "groundnut oil cake": 1.0,
    "cotton seed": 0.9,
    "pelleted": 0.9,
    "rice bran": 0.85,
    "cholam dry": 0.45,
    "cholam": 0.5,
    "rice straw": 0.3,
}

# No single feed should provide more than this share of a ration's nutrients.
MAX_FEED_SHARE = 0.7

# Quick change options for the feed simulator.
SIM_CHANGE_OPTIONS = ["+5", "+10", "+20", "+50", "-10", "-20"]


class FeedState(rx.State):
    """Manages feed types, inventory, daily feeding, plans, and intelligence."""

    feed_types: list[FeedType] = []
    inventory: list[FeedStock] = []
    consumptions: list[FeedConsumption] = []
    feeding_plans: list[FeedingPlan] = []

    # ── Daily feeding form ────────────────────────────────────────────
    feeding_animal_id: str = ""
    feeding_feed_type_id: str = ""
    feeding_qty_str: str = "0"
    feeding_time_of_day: str = "Morning"
    feeding_notes: str = ""
    feeding_date: str = datetime.date.today().isoformat()
    show_feeding_dialog: bool = False
    feeding_success: str = ""

    # ── Quick-nav active section (highlight current pill) ────────────
    active_section: str = "feed-overview"
    # Top-level view: "operations" (daily tasks) | "analytics" (charts/intel).
    active_view: str = "operations"

    # ── Stock form ────────────────────────────────────────────────────
    stock_feed_type_id: str = ""
    stock_quantity_str: str = ""
    stock_unit: str = "kg"
    stock_purchase_date: str = datetime.date.today().isoformat()
    stock_supplier: str = ""
    stock_cost_str: str = ""
    stock_expiry_date: str = ""
    show_stock_dialog: bool = False

    # ── Feed type form ────────────────────────────────────────────────
    new_feed_name: str = ""
    new_feed_category: str = "Concentrate"
    new_feed_unit: str = "kg"
    new_feed_cost_str: str = ""
    show_feed_type_dialog: bool = False

    # ── Plan form ─────────────────────────────────────────────────────
    plan_category: str = "Lactating Cow"
    plan_morning_feed_id: str = ""
    plan_morning_qty_str: str = ""
    plan_evening_feed_id: str = ""
    plan_evening_qty_str: str = ""
    plan_minerals: str = ""
    plan_water_reminder: bool = True
    show_plan_dialog: bool = False

    # ── Ration optimizer ──────────────────────────────────────────────
    ration_category: str = "Lactating Cow"

    # ── Feed simulator ────────────────────────────────────────────────
    sim_feed_type_id: str = ""
    sim_change_str: str = "10"
    sim_animal_id: str = ""  # empty = all animals

    # ── Report ────────────────────────────────────────────────────────
    generated_report_url: str = ""

    # ── Crops → feed stock sync (crop_id → quantity already moved) ────
    crop_sync_markers: dict[str, float] = {}

    # ── Helpers ───────────────────────────────────────────────────────

    def _feed_type_map(self) -> dict[str, FeedType]:
        return {ft["id"]: ft for ft in self.feed_types}

    def _stock_map(self) -> dict[str, FeedStock]:
        return {s["id"]: s for s in self.inventory}

    @rx.var
    def feed_type_options(self) -> list[dict]:
        return [
            {"id": ft["id"], "label": f"{ft['name']} ({ft['unit']})"}
            for ft in self.feed_types
        ]

    @rx.var
    def feeding_qty(self) -> float:
        try:
            value = self.feeding_qty_str
            if not isinstance(value, str):
                value = "0"
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @rx.var
    def stock_quantity(self) -> float:
        try:
            return float(self.stock_quantity_str or 0)
        except ValueError:
            return 0.0

    @rx.var
    def stock_cost(self) -> float:
        try:
            return float(self.stock_cost_str or 0)
        except ValueError:
            return 0.0

    @rx.var
    def new_feed_cost(self) -> float:
        try:
            return float(self.new_feed_cost_str or 0)
        except ValueError:
            return 0.0

    @rx.var
    def plan_morning_qty(self) -> float:
        try:
            return float(self.plan_morning_qty_str or 0)
        except ValueError:
            return 0.0

    @rx.var
    def plan_evening_qty(self) -> float:
        try:
            return float(self.plan_evening_qty_str or 0)
        except ValueError:
            return 0.0

    # ── Data loading ──────────────────────────────────────────────────

    @rx.event
    async def fetch_feed_data(self):
        auth = await self.get_state(AuthState)
        await crud.ensure_farm_seed("feed_types", auth.farm_id, DEFAULT_FEED_TYPES)
        self.feed_types = await crud.get_feed_types(farm_id=auth.farm_id)
        self.inventory = await crud.get_feed_stock(farm_id=auth.farm_id)
        self.consumptions = await crud.get_feed_consumptions(farm_id=auth.farm_id)
        self.feeding_plans = await crud.get_feeding_plans(farm_id=auth.farm_id)
        self.crop_sync_markers = await crud.get_feed_sync_markers(farm_id=auth.farm_id)

    # ── Feed type CRUD ────────────────────────────────────────────────

    @rx.event
    def toggle_feed_type_dialog(self, open: bool):
        self.show_feed_type_dialog = open

    @rx.event
    def set_new_feed_name(self, value: str):
        self.new_feed_name = value

    @rx.event
    def set_new_feed_category(self, value: str):
        self.new_feed_category = value

    @rx.event
    def set_new_feed_unit(self, value: str):
        self.new_feed_unit = value

    @rx.event
    def set_new_feed_cost(self, value: str):
        self.new_feed_cost_str = value

    @rx.event
    async def add_feed_type(self):
        if not self.new_feed_name.strip():
            return rx.toast.error("Feed name is required.")
        auth = await self.get_state(AuthState)
        import uuid

        feed_type: FeedType = {
            "id": str(uuid.uuid4()),
            "name": self.new_feed_name.strip(),
            "category": self.new_feed_category,
            "unit": self.new_feed_unit,
            "cost_per_unit": self.new_feed_cost,
            "is_custom": True,
            "farm_id": auth.farm_id,
        }
        if await crud.create_feed_type(feed_type):
            self.feed_types.append(feed_type)
            self.show_feed_type_dialog = False
            self.new_feed_name = ""
            self.new_feed_cost_str = ""
            return rx.toast.success(f"Added feed type '{feed_type['name']}'.")
        return rx.toast.error("Failed to save feed type.")

    # ── Inventory CRUD ────────────────────────────────────────────────

    @rx.event
    def toggle_stock_dialog(self, open: bool):
        self.show_stock_dialog = open

    @rx.event
    def set_stock_feed_type_id(self, value: str):
        self.stock_feed_type_id = value
        ft = self._feed_type_map().get(value)
        if ft:
            self.stock_unit = ft["unit"]

    @rx.event
    def set_stock_quantity(self, value: str):
        self.stock_quantity_str = value

    @rx.event
    def set_stock_unit(self, value: str):
        self.stock_unit = value

    @rx.event
    def set_stock_purchase_date(self, value: str):
        self.stock_purchase_date = value

    @rx.event
    def set_stock_supplier(self, value: str):
        self.stock_supplier = value

    @rx.event
    def set_stock_cost(self, value: str):
        self.stock_cost_str = value

    @rx.event
    def set_stock_expiry_date(self, value: str):
        self.stock_expiry_date = value

    @rx.event
    async def add_stock(self):
        if not self.stock_feed_type_id or self.stock_quantity <= 0:
            return rx.toast.error("Feed type and quantity are required.")
        ft = self._feed_type_map().get(self.stock_feed_type_id)
        if not ft:
            return rx.toast.error("Unknown feed type.")
        auth = await self.get_state(AuthState)
        import uuid

        stock: FeedStock = {
            "id": str(uuid.uuid4()),
            "feed_type_id": ft["id"],
            "feed_name": ft["name"],
            "quantity": self.stock_quantity,
            "unit": self.stock_unit,
            "purchase_date": self.stock_purchase_date,
            "supplier": self.stock_supplier,
            "cost": self.stock_cost,
            "expiry_date": self.stock_expiry_date or None,
            "farm_id": auth.farm_id,
        }
        if await crud.create_feed_stock(stock):
            self.inventory.append(stock)
            self.show_stock_dialog = False
            self.stock_quantity_str = ""
            self.stock_supplier = ""
            self.stock_cost_str = ""
            self.stock_expiry_date = ""
            return rx.toast.success("Stock added.")
        return rx.toast.error("Failed to save stock.")

    # ── Crops → feed stock ────────────────────────────────────────────

    @staticmethod
    def _is_fodder_crop(name: str) -> bool:
        low = name.lower()
        return any(keyword in low for keyword in FODDER_KEYWORDS)

    @staticmethod
    def _normalize_unit(unit: str) -> str:
        return unit if unit in FEED_UNITS else "kg"

    def _match_feed_type_for_crop(self, crop_name: str) -> FeedType | None:
        """Reuse an existing feed type whose name overlaps the crop name.

        Home Grown (fodder) types are preferred over concentrates so a crop
        like "Rice" links to Rice Straw, not Rice Bran.
        """
        low = crop_name.lower().strip()

        def _find(category: str) -> FeedType | None:
            for ft in self.feed_types:
                if ft["category"] != category:
                    continue
                ftl = ft["name"].lower()
                if low in ftl or ftl.split(" (")[0].strip() in low:
                    return ft
            return None

        return _find("Home Grown") or _find("Concentrate")

    def _build_homegrown_summary(self, crops: list[dict]) -> list[dict]:
        """Fodder crops with harvests and how much is available to move."""
        rows = []
        for crop in crops:
            name = crop.get("name", "")
            if not self._is_fodder_crop(name):
                continue
            harvests = [
                h
                for h in crop.get("harvests", [])
                if float(h.get("quantity", 0)) > 0
            ]
            if not harvests:
                continue
            # Use the unit group with the largest total so mixed-unit harvests
            # don't produce a meaningless sum (kg + bundles).
            by_unit: dict[str, float] = defaultdict(float)
            for h in harvests:
                u = self._normalize_unit(h.get("unit", "kg"))
                by_unit[u] += float(h.get("quantity", 0))
            unit = max(by_unit, key=by_unit.get)
            harvested = round(by_unit[unit], 2)
            moved = round(self.crop_sync_markers.get(crop["id"], 0.0), 2)
            delta = round(harvested - moved, 2)
            ft = self._match_feed_type_for_crop(name)
            rows.append(
                {
                    "crop_id": crop["id"],
                    "name": name,
                    "unit": unit,
                    "harvested": harvested,
                    "moved": moved,
                    "delta": delta,
                    "feed_type_name": ft["name"] if ft else f"{name} (Harvested)",
                    "synced": delta <= 0,
                    "available": delta > 0,
                }
            )
        return rows

    @rx.var
    async def homegrown_summary(self) -> list[dict]:
        cs = await self.get_state(CropState)
        return self._build_homegrown_summary(cs.crops_list)

    async def _sync_crop_to_stock(
        self, crop: dict, farm_id: str
    ) -> tuple[bool, str]:
        """Move one crop's new harvests into feed stock (idempotent).

        Returns ``(moved, message)`` — ``moved`` is True only when stock was
        actually added. Safe to call repeatedly: synced harvests are skipped
        via the persisted ``crop_sync_markers``.
        """
        harvests = [
            h for h in crop.get("harvests", []) if float(h.get("quantity", 0)) > 0
        ]
        if not harvests:
            return False, f"No harvests recorded for {crop['name']} yet."
        by_unit: dict[str, float] = defaultdict(float)
        for h in harvests:
            u = self._normalize_unit(h.get("unit", "kg"))
            by_unit[u] += float(h.get("quantity", 0))
        unit = max(by_unit, key=by_unit.get)
        harvested = round(by_unit[unit], 2)
        moved = self.crop_sync_markers.get(crop["id"], 0.0)
        delta = round(harvested - moved, 2)
        if delta <= 0:
            return False, f"{crop['name']} harvest is already in feed stock."

        import uuid

        ft = self._match_feed_type_for_crop(crop["name"])
        if not ft:
            ft = {
                "id": str(uuid.uuid4()),
                "name": f"{crop['name']} (Harvested)",
                "category": "Home Grown",
                "unit": unit,
                "cost_per_unit": 0.0,
                "is_custom": True,
                "farm_id": farm_id,
            }
            if not await crud.create_feed_type(ft):
                return False, "Could not save feed type for this crop."
            self.feed_types.append(ft)

        # Add to the existing harvest batch if there is one, else create one.
        batch = next(
            (
                s
                for s in self.inventory
                if s["feed_type_id"] == ft["id"] and s.get("supplier") == "Harvest"
            ),
            None,
        )
        if batch:
            batch["quantity"] = round(batch["quantity"] + delta, 2)
            await crud.update_feed_stock(batch["id"], {"quantity": batch["quantity"]})
        else:
            stock: FeedStock = {
                "id": str(uuid.uuid4()),
                "feed_type_id": ft["id"],
                "feed_name": ft["name"],
                "quantity": delta,
                "unit": unit,
                "purchase_date": datetime.date.today().isoformat(),
                "supplier": "Harvest",
                "cost": 0.0,
                "expiry_date": None,
                "farm_id": farm_id,
            }
            if not await crud.create_feed_stock(stock):
                return False, "Could not save stock."
            self.inventory.append(stock)

        self.crop_sync_markers[crop["id"]] = harvested
        await crud.set_feed_sync_marker(farm_id, crop["id"], str(harvested))
        return True, f"Moved {delta} {unit} of {crop['name']} into feed stock."

    async def _auto_sync_crops(self, crops: list[dict], farm_id: str) -> int:
        """Move every fodder crop's new harvests into stock; returns count."""
        count = 0
        for crop in crops:
            if not self._is_fodder_crop(crop.get("name", "")):
                continue
            if not crop.get("harvests"):
                continue
            moved, _ = await self._sync_crop_to_stock(crop, farm_id)
            if moved:
                count += 1
        return count

    @rx.event
    async def auto_sync_homegrown_crops(self):
        """Auto-move all new fodder crop harvests into feed stock on page load."""
        cs = await self.get_state(CropState)
        auth = await self.get_state(AuthState)
        count = await self._auto_sync_crops(cs.crops_list, auth.farm_id)
        if count:
            return rx.toast.success(
                f"Auto-synced {count} fodder crop(s) into feed stock."
            )
        return None

    # ── Daily feeding ─────────────────────────────────────────────────

    @rx.event
    def toggle_feeding_dialog(self, open: bool):
        self.show_feeding_dialog = open
        self.feeding_success = ""

    @rx.event
    def set_active_section(self, section_id: str):
        """Highlight the quick-nav pill the user just tapped."""
        self.active_section = section_id

    @rx.event
    def switch_view(self, view: str):
        """Switch between the Operations and Analytics views of the Feed page."""
        if view in ("operations", "analytics"):
            self.active_view = view
        self.active_section = (
            "feed-overview" if self.active_view == "operations" else "feed-stats"
        )

    @rx.event
    def set_feeding_animal_id(self, value: str):
        self.feeding_animal_id = value

    @rx.event
    def set_feeding_feed_type_id(self, value: str):
        self.feeding_feed_type_id = value

    @rx.event
    def set_feeding_time_of_day(self, value: str):
        self.feeding_time_of_day = value

    @rx.event
    def set_feeding_notes(self, value: str):
        self.feeding_notes = value

    @rx.event
    def set_feeding_date(self, value: str):
        self.feeding_date = value

    def _safe_qty_str(self) -> str:
        """Return feeding_qty_str coerced to a plain string (never a dict)."""
        value = self.feeding_qty_str
        if not isinstance(value, str):
            value = "0"
        return value

    @rx.event
    def handle_feeding_keypad(self, key: str):
        key = key if isinstance(key, str) else ""
        current = self._safe_qty_str()
        if key == "del":
            current = current[:-1] if len(current) > 1 else "0"
        elif key == ".":
            if "." not in current:
                current += "."
        elif current == "0":
            current = key
        else:
            current += key
        self.feeding_qty_str = current

    @rx.event
    def quick_add_feeding_qty(self, value: str):
        """Quick-add to the quantity (value arrives as a string like '+0.5')."""
        try:
            added = float(value)
        except (TypeError, ValueError):
            added = 0.0
        base = float(self._safe_qty_str() or 0)
        self.feeding_qty_str = str(round(base + added, 2))

    @rx.event
    async def record_feeding(self):
        """Record today's feeding for an animal (deducts stock)."""
        if not self.feeding_animal_id or not self.feeding_feed_type_id:
            return rx.toast.error("Select animal and feed type first.")
        if self.feeding_qty <= 0:
            return rx.toast.error("Quantity must be positive.")
        ft = self._feed_type_map().get(self.feeding_feed_type_id)
        if not ft:
            return rx.toast.error("Unknown feed type.")
        auth = await self.get_state(AuthState)
        cs = await self.get_state(CattleState)
        import uuid

        animal = next(
            (c for c in cs.cattle_list if c["id"] == self.feeding_animal_id), None
        )
        animal_name = animal["name"] if animal else "Unknown"

        consumption: FeedConsumption = {
            "id": str(uuid.uuid4()),
            "date": self.feeding_date,
            "time_of_day": self.feeding_time_of_day,
            "animal_id": self.feeding_animal_id,
            "animal_name": animal_name,
            "feed_type_id": ft["id"],
            "feed_name": ft["name"],
            "quantity": self.feeding_qty,
            "unit": ft["unit"],
            "notes": self.feeding_notes,
            "farm_id": auth.farm_id,
        }
        if await crud.create_feed_consumption(consumption):
            self.consumptions.append(consumption)
            # Deduct from stock (earliest-expiring batch first).
            self._deduct_stock(ft["id"], self.feeding_qty)
            self.feeding_success = (
                f"✓ {animal_name} · {self.feeding_qty} {ft['unit']} {ft['name']}"
            )
            self.feeding_qty_str = "0"
            return rx.toast.success("Feeding recorded.")
        return rx.toast.error("Failed to save feeding.")

    async def _deduct_stock(self, feed_type_id: str, qty: float) -> None:
        """Reduce stock quantity for a feed type (FIFO by expiry date)."""
        batches = [
            s
            for s in self.inventory
            if s["feed_type_id"] == feed_type_id and s["quantity"] > 0
        ]
        batches.sort(
            key=lambda s: (s.get("expiry_date") or "9999-12-31", s["purchase_date"])
        )
        remaining = qty
        for batch in batches:
            if remaining <= 0:
                break
            take = min(batch["quantity"], remaining)
            batch["quantity"] = round(batch["quantity"] - take, 3)
            remaining = round(remaining - take, 3)
            await crud.update_feed_stock(batch["id"], {"quantity": batch["quantity"]})

    # ── Feeding plans ─────────────────────────────────────────────────

    @rx.event
    def toggle_plan_dialog(self, open: bool):
        self.show_plan_dialog = open

    @rx.event
    def set_plan_category(self, value: str):
        self.plan_category = value

    @rx.event
    def set_plan_morning_feed_id(self, value: str):
        self.plan_morning_feed_id = value

    @rx.event
    def set_plan_morning_qty(self, value: str):
        self.plan_morning_qty_str = value

    @rx.event
    def set_plan_evening_feed_id(self, value: str):
        self.plan_evening_feed_id = value

    @rx.event
    def set_plan_evening_qty(self, value: str):
        self.plan_evening_qty_str = value

    @rx.event
    def set_plan_minerals(self, value: str):
        self.plan_minerals = value

    @rx.event
    def set_plan_water_reminder(self, value: bool):
        self.plan_water_reminder = value

    @rx.event
    async def create_plan(self):
        if not self.plan_morning_feed_id or self.plan_morning_qty <= 0:
            return rx.toast.error("Morning feed and quantity are required.")
        auth = await self.get_state(AuthState)
        import uuid

        ft_map = self._feed_type_map()
        morning_ft = ft_map.get(self.plan_morning_feed_id)
        evening_ft = ft_map.get(self.plan_evening_feed_id)
        plan: FeedingPlan = {
            "id": str(uuid.uuid4()),
            "category": self.plan_category,
            "name": f"{self.plan_category} Plan",
            "morning": [
                {
                    "feed_type_id": morning_ft["id"],
                    "feed_name": morning_ft["name"],
                    "quantity": self.plan_morning_qty,
                    "unit": morning_ft["unit"],
                }
            ],
            "evening": (
                [
                    {
                        "feed_type_id": evening_ft["id"],
                        "feed_name": evening_ft["name"],
                        "quantity": self.plan_evening_qty,
                        "unit": evening_ft["unit"],
                    }
                ]
                if evening_ft and self.plan_evening_qty > 0
                else []
            ),
            "minerals": self.plan_minerals,
            "water_reminder": self.plan_water_reminder,
            "farm_id": auth.farm_id,
        }
        if await crud.create_feeding_plan(plan):
            self.feeding_plans.append(plan)
            self.show_plan_dialog = False
            self.plan_morning_qty_str = ""
            self.plan_evening_qty_str = ""
            return rx.toast.success("Feeding plan created.")
        return rx.toast.error("Failed to save plan.")

    # ── Analytics: consumption & cost ─────────────────────────────────

    def _consumptions_in_range(self, days: int) -> list[FeedConsumption]:
        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        return [
            c
            for c in self.consumptions
            if c["date"] >= cutoff.isoformat()
        ]

    @rx.var
    def daily_consumption_kg(self) -> float:
        return round(
            sum(
                c["quantity"]
                for c in self._consumptions_in_range(1)
                if c["unit"] == "kg"
            ),
            2,
        )

    @rx.var
    def weekly_consumption_kg(self) -> float:
        return round(
            sum(
                c["quantity"]
                for c in self._consumptions_in_range(7)
                if c["unit"] == "kg"
            ),
            2,
        )

    @rx.var
    def monthly_consumption_kg(self) -> float:
        return round(
            sum(
                c["quantity"]
                for c in self._consumptions_in_range(30)
                if c["unit"] == "kg"
            ),
            2,
        )

    @rx.var
    async def monthly_feed_cost(self) -> float:
        """Feed cost this month = recorded consumption cost (₹)."""
        ts = await self.get_state(TransactionState)
        ft_map = self._feed_type_map()
        consumption_cost = sum(
            c["quantity"] * ft_map.get(c["feed_type_id"], {}).get("cost_per_unit", 0)
            for c in self._consumptions_in_range(30)
        )
        # Feed purchase expenses recorded as transactions.
        month = datetime.date.today().replace(day=1).isoformat()
        purchase_cost = sum(
            float(t["amount"])
            for t in ts.transactions
            if t["type"] == "expense"
            and t["category"]["name"] == "Cattle Feed"
            and t["date"] >= month
        )
        return round(consumption_cost + purchase_cost, 2)

    @rx.var
    async def monthly_milk_liters(self) -> float:
        cs = await self.get_state(CattleState)
        cutoff = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
        total = 0.0
        for cattle in cs.cattle_list:
            for rec in cattle.get("milk_production", []):
                if rec["date"] >= cutoff:
                    total += float(rec.get("liters", 0))
        return round(total, 1)

    @rx.var
    async def feed_cost_per_liter(self) -> float:
        liters = await self.monthly_milk_liters
        if liters <= 0:
            return 0.0
        return round(await self.monthly_feed_cost / liters, 2)

    @rx.var
    def feed_cost_trend(self) -> list[dict]:
        """Monthly feed cost trend (last 6 months) from consumption records."""
        ft_map = self._feed_type_map()
        monthly: dict[str, float] = defaultdict(float)
        today = datetime.date.today()
        for c in self.consumptions:
            try:
                month_key = datetime.date.fromisoformat(c["date"]).strftime("%Y-%m")
            except ValueError:
                continue
            monthly[month_key] += c["quantity"] * ft_map.get(c["feed_type_id"], {}).get("cost_per_unit", 0)
        data = []
        for i in range(5, -1, -1):
            month = today.replace(day=1) - datetime.timedelta(days=30 * i)
            key = month.strftime("%Y-%m")
            data.append({"month": month.strftime("%b"), "cost": round(monthly[key], 2)})
        return data

    @rx.var
    def consumption_by_feed(self) -> list[dict]:
        """Consumption + cost grouped by feed type (last 30 days)."""
        ft_map = self._feed_type_map()
        totals: dict[str, dict] = defaultdict(lambda: {"qty": 0.0, "cost": 0.0})
        for c in self._consumptions_in_range(30):
            ft = ft_map.get(c["feed_type_id"], {})
            totals[c["feed_name"]]["qty"] += c["quantity"]
            totals[c["feed_name"]]["cost"] += c["quantity"] * ft.get("cost_per_unit", 0)
        max_qty = max((v["qty"] for v in totals.values()), default=0) or 1
        return [
            {
                "name": name,
                "qty": round(v["qty"], 1),
                "cost": round(v["cost"], 2),
                "pct": round(min(v["qty"] / max_qty, 1) * 100),
            }
            for name, v in sorted(totals.items(), key=lambda kv: kv[1]["cost"], reverse=True)
        ]

    # ── Milk vs Feed analysis ─────────────────────────────────────────

    def _animal_avg_milk(self, cattle: dict, days: int) -> float:
        cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
        recs = [r for r in cattle.get("milk_production", []) if r["date"] >= cutoff]
        if not recs:
            return 0.0
        return sum(float(r.get("liters", 0)) for r in recs) / len(recs)

    def _animal_feed_kg(self, animal_id: str, days: int) -> float:
        cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
        return sum(
            c["quantity"]
            for c in self.consumptions
            if c["animal_id"] == animal_id and c["date"] >= cutoff and c["unit"] == "kg"
        )

    def _animal_feed_cost(self, animal_id: str, days: int) -> float:
        cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
        ft_map = self._feed_type_map()
        return sum(
            c["quantity"] * ft_map.get(c["feed_type_id"], {}).get("cost_per_unit", 0)
            for c in self.consumptions
            if c["animal_id"] == animal_id and c["date"] >= cutoff
        )

    @rx.var
    async def milk_feed_insights(self) -> list[dict]:
        cs = await self.get_state(CattleState)
        return self._build_milk_feed_insights(cs.cattle_list)

    def _build_milk_feed_insights(self, cattle_list: list[dict]) -> list[dict]:
        """Milk vs feed insight lines (sync — testable, no state lookups)."""
        insights = []
        # 1) Milk change per animal
        for cattle in cattle_list:
            recents = self._animal_avg_milk(cattle, 7)
            previous = self._animal_avg_milk(cattle, 14)
            if previous > 0 and recents > 0:
                change = (recents - previous) / previous * 100
                feed_kg = self._animal_feed_kg(cattle["id"], 7)
                if change >= 8:
                    insights.append(
                        {
                            "icon": "📈",
                            "color": "text-emerald-600",
                            "text": (
                                f"{cattle['name']} milk up {change:.0f}% "
                                f"({previous:.1f}→{recents:.1f} L). Keep current feeding."
                            ),
                        }
                    )
                elif change <= -8:
                    insights.append(
                        {
                            "icon": "📉",
                            "color": "text-red-600",
                            "text": (
                                f"{cattle['name']} milk down {abs(change):.0f}%. "
                                f"{'Check feed intake and health.' if feed_kg <= 0 else 'Review feed quality or add concentrates.'}"
                            ),
                        }
                    )
        # 2) Best feed per ₹ spent
        ft_map = self._feed_type_map()
        by_feed: dict[str, dict] = defaultdict(lambda: {"liters": 0.0, "cost": 0.0})
        for c in self._consumptions_in_range(30):
            ft = ft_map.get(c["feed_type_id"], {})
            by_feed[c["feed_name"]]["cost"] += c["quantity"] * ft.get("cost_per_unit", 0)
        for cattle in cattle_list:
            for c in self.consumptions:
                if c["animal_id"] == cattle["id"]:
                    by_feed[c["feed_name"]]["liters"] += self._animal_avg_milk(cattle, 30)
        ranked = sorted(
            by_feed.items(),
            key=lambda kv: (kv[1]["liters"] / kv[1]["cost"]) if kv[1]["cost"] > 0 else 0,
            reverse=True,
        )
        if ranked and ranked[0][1]["cost"] > 0:
            best_name, best = ranked[0]
            insights.append(
                {
                    "icon": "🏆",
                    "color": "text-emerald-600",
                    "text": f"{best_name} gives the best milk output per ₹ spent.",
                }
            )
        # 3) High intake, low milk
        for cattle in cattle_list:
            feed_kg = self._animal_feed_kg(cattle["id"], 7)
            milk = self._animal_avg_milk(cattle, 7)
            if feed_kg > 0 and milk > 0 and (milk / feed_kg) < 0.3:
                insights.append(
                    {
                        "icon": "⚠️",
                        "color": "text-orange-600",
                        "text": (
                            f"{cattle['name']} eats {feed_kg:.1f} kg feed but produces "
                            f"only {milk:.1f} L. Check for waste or health issues."
                        ),
                    }
                )
        return insights[:8]

    # ── Feed Conversion Efficiency ────────────────────────────────────

    @rx.var
    async def efficiency_ranks(self) -> list[dict]:
        cs = await self.get_state(CattleState)
        return self._build_efficiency_ranks(cs.cattle_list)

    def _build_efficiency_ranks(self, cattle_list: list[dict]) -> list[dict]:
        """Rank animals by feed conversion (sync — testable)."""
        rows = []
        for cattle in cattle_list:
            milk = self._animal_avg_milk(cattle, 7)
            feed_kg = self._animal_feed_kg(cattle["id"], 7)
            feed_cost = self._animal_feed_cost(cattle["id"], 7)
            if milk <= 0 or feed_kg <= 0:
                continue
            milk_per_kg = milk / feed_kg
            milk_per_rupee = (milk * MILK_PRICE_PER_LITER) / feed_cost if feed_cost > 0 else 0
            score = round(min(100, max(0, milk_per_kg * 45)), 1)
            if score >= 70:
                rank = "Excellent"
            elif score >= 55:
                rank = "Good"
            elif score >= 40:
                rank = "Average"
            else:
                rank = "Needs Attention"
            rows.append(
                {
                    "id": cattle["id"],
                    "name": cattle["name"],
                    "image_url": cattle["image_url"],
                    "milk_per_kg": round(milk_per_kg, 2),
                    "milk_per_rupee": round(milk_per_rupee, 2),
                    "score": score,
                    "rank": rank,
                }
            )
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows

    @rx.var
    async def best_performing_cow(self) -> dict:
        ranks = await self.efficiency_ranks
        return ranks[0] if ranks else {}

    @rx.var
    async def milk_feed_chart_data(self) -> list[dict]:
        """Per-animal milk L/day (7d avg) vs feed kg/7d for the comparison chart."""
        cs = await self.get_state(CattleState)
        rows = []
        for c in cs.cattle_list:
            milk = self._animal_avg_milk(c, 7)
            feed = self._animal_feed_kg(c["id"], 7)
            if milk <= 0 and feed <= 0:
                continue
            rows.append(
                {"name": c["name"], "milk": round(milk, 1), "feed": round(feed / 7, 1)}
            )
        return rows

    @rx.var
    async def efficiency_chart_data(self) -> list[dict]:
        """Efficiency scores per animal for the score chart."""
        ranks = await self.efficiency_ranks
        return [{"name": r["name"], "score": r["score"]} for r in ranks]

    # ── AI Nutrition Advisor (rule-based) ─────────────────────────────

    @rx.var
    async def ai_recommendations(self) -> list[dict]:
        cs = await self.get_state(CattleState)
        return self._build_recommendations(cs.cattle_list)

    def _build_recommendations(self, cattle_list: list[dict]) -> list[dict]:
        """Rule-based AI nutrition advisor (sync — testable, works offline)."""
        recs = []
        concentrates = [ft for ft in self.feed_types if ft["category"] == "Concentrate"]
        green = [
            ft
            for ft in self.feed_types
            if "fodder" in ft["name"].lower() or "cholam" in ft["name"].lower()
        ]
        concentrate_ft = concentrates[0] if concentrates else None
        green_ft = green[0] if green else None

        for cattle in cattle_list:
            milk = self._animal_avg_milk(cattle, 7)
            feed_kg = self._animal_feed_kg(cattle["id"], 7)
            feed_cost = self._animal_feed_cost(cattle["id"], 7)
            if milk <= 0:
                continue
            if concentrate_ft and feed_kg > 0:
                conc_kg = sum(
                    c["quantity"]
                    for c in self.consumptions
                    if c["animal_id"] == cattle["id"]
                    and c["date"] >= (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
                    and c["feed_type_id"] in {f["id"] for f in concentrates}
                )
                conc_share = conc_kg / feed_kg
                if milk >= 15 and conc_share < 0.4:
                    boost = 0.5 if milk < 20 else 0.8
                    recs.append(
                        {
                            "animal": cattle["name"],
                            "icon": "📈",
                            "color": "bg-emerald-50 text-emerald-800 border-emerald-200",
                            "title": f"Increase {concentrate_ft['name']}",
                            "action": (
                                f"{cattle['name']} produces {milk:.1f} L/day. Increase "
                                f"{concentrate_ft['name']} by {int(boost * 1000)} g/day. "
                                f"Expected milk gain: +{boost} to +{boost + 0.4:.1f} L/day."
                            ),
                        }
                    )
                elif conc_share > 0.6:
                    recs.append(
                        {
                            "animal": cattle["name"],
                            "icon": "⚠️",
                            "color": "bg-orange-50 text-orange-800 border-orange-200",
                            "title": "Reduce concentrate",
                            "action": (
                                f"{cattle['name']} gets {conc_share:.0%} concentrate. "
                                "Excess concentrate can upset digestion. Reduce by ~10% and add green fodder."
                            ),
                        }
                    )
            if green_ft:
                green_kg = sum(
                    c["quantity"]
                    for c in self.consumptions
                    if c["animal_id"] == cattle["id"]
                    and c["feed_type_id"] == green_ft["id"]
                    and c["date"] >= (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
                )
                if feed_kg > 0 and (green_kg / feed_kg) < 0.2:
                    recs.append(
                        {
                            "animal": cattle["name"],
                            "icon": "🌱",
                            "color": "bg-green-50 text-green-800 border-green-200",
                            "title": "Increase green fodder",
                            "action": (
                                f"{cattle['name']} needs more green fodder (currently <20% of intake). "
                                "Feed 2-3 kg more Cholam/forage daily for better milk fat and health."
                            ),
                        }
                    )
            if milk > 0 and feed_cost > 0 and (milk * MILK_PRICE_PER_LITER) / feed_cost < 1.2:
                recs.append(
                    {
                        "animal": cattle["name"],
                        "icon": "💰",
                        "color": "bg-yellow-50 text-yellow-800 border-yellow-200",
                        "title": "Balance protein & energy",
                        "action": (
                            f"{cattle['name']} feed cost is high vs milk value. "
                            "Swap part of costly concentrate for groundnut oil cake or reduce wastage."
                        ),
                    }
                )
        return recs[:6]

    # ── Smart alerts ──────────────────────────────────────────────────

    @rx.var
    def smart_alerts(self) -> list[dict]:
        alerts = []
        # Stock levels
        for stock in self.inventory:
            if stock["quantity"] <= 0:
                alerts.append(
                    {
                        "icon": "⛔",
                        "color": "text-red-600 bg-red-50",
                        "title": "Out of stock",
                        "text": f"{stock['feed_name']} is out of stock. Order soon.",
                    }
                )
            elif stock["quantity"] < 10:
                alerts.append(
                    {
                        "icon": "⚠️",
                        "color": "text-yellow-600 bg-yellow-50",
                        "title": "Low stock",
                        "text": f"{stock['feed_name']} is low ({stock['quantity']} {stock['unit']}).",
                    }
                )
            if stock.get("expiry_date"):
                try:
                    days = (datetime.date.fromisoformat(stock["expiry_date"]) - datetime.date.today()).days
                    if 0 <= days <= 7:
                        alerts.append(
                            {
                                "icon": "⏰",
                                "color": "text-orange-600 bg-orange-50",
                                "title": "Expiring soon",
                                "text": f"{stock['feed_name']} expires in {days} day(s). Use it first.",
                            }
                        )
                except ValueError:
                    pass
        # Consumption spike vs previous week
        this_week = sum(c["quantity"] for c in self._consumptions_in_range(7))
        prev_week = sum(c["quantity"] for c in self._consumptions_in_range(14)) - this_week
        if prev_week > 0 and this_week > prev_week * 1.3:
            alerts.append(
                {
                    "icon": "🔥",
                    "color": "text-red-600 bg-red-50",
                    "title": "Consumption spike",
                    "text": f"Feed use is up {(this_week / prev_week - 1) * 100:.0f}% this week.",
                }
            )
        return alerts[:8]

    # ── Purchase planner ──────────────────────────────────────────────

    @rx.var
    def purchase_suggestions(self) -> list[dict]:
        suggestions = []
        remaining: dict[str, float] = defaultdict(float)
        for stock in self.inventory:
            remaining[stock["feed_type_id"]] += stock["quantity"]
        daily_use: dict[str, float] = defaultdict(float)
        for c in self._consumptions_in_range(7):
            daily_use[c["feed_type_id"]] += c["quantity"] / 7
        for ft in self.feed_types:
            rem = remaining.get(ft["id"], 0)
            rate = daily_use.get(ft["id"], 0)
            if rate <= 0:
                continue
            days_left = rem / rate
            if days_left <= 14:
                buy_qty = round(max(rate * 14 - rem, rate * 7), 1)
                suggestions.append(
                    {
                        "name": ft["name"],
                        "remaining": round(rem, 1),
                        "days_left": round(days_left, 1),
                        "buy_qty": buy_qty,
                        "unit": ft["unit"],
                        "text": (
                            f"{ft['name']} will last ~{days_left:.0f} days. "
                            f"Buy {buy_qty} {ft['unit']} next week."
                        ),
                    }
                )
        return sorted(suggestions, key=lambda s: s["days_left"])[:6]

    # ── Ration optimizer (cheapest balanced ration) ──────────────────

    @rx.event
    def set_ration_category(self, value: str):
        self.ration_category = value

    def _nutrient_score(self, ft: FeedType) -> float:
        """Rough nutrient density per kg based on the feed name."""
        low = ft["name"].lower()
        for keyword, score in NUTRIENT_SCORES.items():
            if keyword in low:
                return score
        return 0.5

    @rx.var
    def cheapest_ration(self) -> dict:
        """Cheapest feed mix covering a group's daily nutrient needs.

        Greedy: cheapest nutrient first, no single feed above MAX_FEED_SHARE
        of the requirement (forces a more balanced mix).
        """
        req = RATION_REQUIREMENTS.get(self.ration_category, 8.0)
        scored = []
        for ft in self.feed_types:
            score = self._nutrient_score(ft)
            if score > 0:
                scored.append((ft, ft["cost_per_unit"] / score))
        scored.sort(key=lambda pair: pair[1])
        if not scored:
            return {"category": self.ration_category, "requirement": req, "items": [], "total_cost": 0.0, "cost_per_unit": 0.0}

        remaining = req
        items = []
        total_cost = 0.0
        for ft, _ in scored:
            if remaining <= 0:
                break
            take_units = min(remaining, req * MAX_FEED_SHARE)
            score = self._nutrient_score(ft)
            qty = round(take_units / score, 2)
            cost = qty * ft["cost_per_unit"]
            items.append(
                {
                    "name": ft["name"],
                    "qty": qty,
                    "unit": ft["unit"],
                    "cost": round(cost, 2),
                    "in_stock": any(
                        s["feed_type_id"] == ft["id"] and s["quantity"] > 0
                        for s in self.inventory
                    ),
                }
            )
            total_cost += cost
            remaining -= take_units
        # Top up with the cheapest feed if the requirement wasn't covered.
        if remaining > 0:
            ft = scored[0][0]
            qty = round(remaining / self._nutrient_score(ft), 2)
            cost = qty * ft["cost_per_unit"]
            items.append(
                {
                    "name": ft["name"],
                    "qty": qty,
                    "unit": ft["unit"],
                    "cost": round(cost, 2),
                    "in_stock": any(
                        s["feed_type_id"] == ft["id"] and s["quantity"] > 0
                        for s in self.inventory
                    ),
                }
            )
            total_cost += cost
        # Merge duplicate feed rows (e.g. single-feed farms: 70% + top-up).
        merged: dict[str, dict] = {}
        for item in items:
            name = item["name"]
            if name in merged:
                merged[name]["qty"] = round(merged[name]["qty"] + item["qty"], 2)
                merged[name]["cost"] = round(merged[name]["cost"] + item["cost"], 2)
                merged[name]["in_stock"] = merged[name]["in_stock"] or item["in_stock"]
            else:
                merged[name] = item
        items = list(merged.values())
        return {
            "category": self.ration_category,
            "requirement": req,
            "items": items,
            "total_cost": round(total_cost, 2),
            "cost_per_unit": round(total_cost / req, 2) if req else 0.0,
        }

    @rx.var
    def cheapest_ration_items(self) -> list[dict]:
        """Typed list of ration items so templates can foreach over them."""
        return self.cheapest_ration.get("items", [])

    # ── Feed simulator ("what if I change feed by X%?") ──────────────

    @rx.var
    def sim_change(self) -> float:
        try:
            return float(self.sim_change_str or 0)
        except ValueError:
            return 0.0

    @rx.event
    def set_sim_feed_type_id(self, value: str):
        self.sim_feed_type_id = value

    @rx.event
    def set_sim_change(self, value: str):
        self.sim_change_str = value

    @rx.event
    def set_sim_animal_id(self, value: str):
        self.sim_animal_id = value

    @rx.var
    async def sim_animal_options(self) -> list[dict]:
        cs = await self.get_state(CattleState)
        return [{"id": "", "label": "All animals"}] + [
            {"id": c["id"], "label": c["name"]} for c in cs.cattle_list
        ]

    def _compute_simulation(
        self, ft: FeedType, change_pct: float, animals: list[dict]
    ) -> dict:
        """Estimate milk / cost / profit effect of changing one feed's quantity.

        Rule of thumb: +1 kg concentrate ≈ +0.8 L milk/day, +1 kg home-grown
        fodder ≈ +0.3 L milk/day. Gains capped at +3 L/day and +25% of current
        milk; reductions capped at -20% of current milk.
        """
        response = 0.8 if ft["category"] == "Concentrate" else 0.3
        # Clamp the adjustment so extreme reductions don't overstate savings.
        change_pct = max(-50.0, min(50.0, change_pct))
        cutoff = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        animal_ids = {a["id"] for a in animals}
        current_qty = sum(
            c["quantity"]
            for c in self.consumptions
            if c["feed_type_id"] == ft["id"]
            and c["animal_id"] in animal_ids
            and c["date"] >= cutoff
        ) / 7.0
        current_milk = sum(self._animal_avg_milk(a, 7) for a in animals)
        delta_qty = current_qty * change_pct / 100.0
        milk_gain = delta_qty * response
        if milk_gain > 0:
            milk_gain = min(milk_gain, min(3.0, current_milk * 0.25))
        else:
            milk_gain = max(milk_gain, -(current_milk * 0.2))
        delta_cost = delta_qty * ft["cost_per_unit"]
        profit = milk_gain * MILK_PRICE_PER_LITER - delta_cost
        if profit > 1.0:
            verdict = "Profitable"
        elif profit < -1.0:
            verdict = "Not profitable"
        else:
            verdict = "Break-even"
        return {
            "feed_name": ft["name"],
            "unit": ft["unit"],
            "animal_label": animals[0]["name"] if len(animals) == 1 else "All animals",
            "current_qty": round(current_qty, 1),
            "new_qty": round(max(current_qty + delta_qty, 0), 1),
            "current_milk": round(current_milk, 1),
            "milk_gain": round(milk_gain, 2),
            "delta_cost": round(delta_cost, 2),
            "profit_change": round(profit, 2),
            "verdict": verdict,
        }

    @rx.var
    async def simulation_results(self) -> dict:
        ft = self._feed_type_map().get(self.sim_feed_type_id)
        if not ft:
            return {}
        cs = await self.get_state(CattleState)
        animals = list(cs.cattle_list)
        if self.sim_animal_id:
            animals = [c for c in animals if c["id"] == self.sim_animal_id]
        if not animals:
            return {}
        return self._compute_simulation(ft, self.sim_change, animals)

    # ── Bulk feeding from plans ───────────────────────────────────────

    @staticmethod
    def _has_recent_milk(cattle: dict, days: int) -> bool:
        cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
        return any(
            r.get("date", "") >= cutoff
            for r in cattle.get("milk_production", [])
            if float(r.get("liters", 0)) > 0
        )

    @staticmethod
    def _match_plan_animals_by_category(
        category: str, cattle_list: list[dict], pregnant_ids: set[str]
    ) -> list[dict]:
        """Which animals belong to a plan category (rule-based)."""
        if category == "Lactating Cow":
            return [c for c in cattle_list if FeedState._has_recent_milk(c, 7)]
        if category == "Dry Cow":
            # A dry cow has lactated before but has no recent milk — this
            # keeps Dry Cow and Heifer groups from overlapping.
            return [
                c
                for c in cattle_list
                if not c.get("is_juvenile")
                and c.get("animal_type") in ("cow", "buffalo")
                and c.get("milk_production")
                and not FeedState._has_recent_milk(c, 7)
            ]
        if category == "Calf":
            return [
                c
                for c in cattle_list
                if c.get("is_juvenile")
                or (c.get("age") is not None and c.get("age") < 1)
            ]
        if category == "Heifer":
            return [
                c
                for c in cattle_list
                if not c.get("is_juvenile")
                and c.get("animal_type") in ("cow", "buffalo")
                and not c.get("milk_production")
            ]
        if category == "Pregnant Cow":
            return [c for c in cattle_list if c["id"] in pregnant_ids]
        if category == "Bull":
            return [c for c in cattle_list if c.get("animal_type") == "bull"]
        return []

    async def _match_plan_animals(self, category: str) -> list[dict]:
        """Animals matching a plan category, using live farm state."""
        cs = await self.get_state(CattleState)
        pregnant_ids: set[str] = set()
        if category == "Pregnant Cow":
            bs = await self.get_state(BreedingState)
            pregnant_ids = {
                cycle["cattle_id"]
                for cycle in bs.breeding_cycles
                if cycle.get("status") == "pregnant"
            }
        return self._match_plan_animals_by_category(
            category, cs.cattle_list, pregnant_ids
        )

    async def _record_plan_for_animals(
        self, plan: dict, animals: list[dict], farm_id: str
    ) -> int:
        """Record morning/evening plan feed for each animal; returns entry count."""
        import uuid

        count = 0
        date = datetime.date.today().isoformat()
        for animal in animals:
            for period, items in (("Morning", plan["morning"]), ("Evening", plan["evening"])):
                for item in items:
                    ft = self._feed_type_map().get(item["feed_type_id"])
                    if not ft:
                        continue
                    consumption: FeedConsumption = {
                        "id": str(uuid.uuid4()),
                        "date": date,
                        "time_of_day": period,
                        "animal_id": animal["id"],
                        "animal_name": animal["name"],
                        "feed_type_id": ft["id"],
                        "feed_name": ft["name"],
                        "quantity": item["quantity"],
                        "unit": ft["unit"],
                        "notes": f"From {plan['name']}",
                        "farm_id": farm_id,
                    }
                    if await crud.create_feed_consumption(consumption):
                        self.consumptions.append(consumption)
                        await self._deduct_stock(ft["id"], item["quantity"])
                        count += 1
        return count

    @rx.event
    async def bulk_feed_plan(self, plan_id: str):
        """Feed every animal matching a plan's category (morning + evening)."""
        auth = await self.get_state(AuthState)
        plan = next((p for p in self.feeding_plans if p["id"] == plan_id), None)
        if not plan:
            return rx.toast.error("Plan not found.")
        animals = await self._match_plan_animals(plan["category"])
        if not animals:
            return rx.toast.info(
                f"No animals currently match the '{plan['category']}' group."
            )
        count = await self._record_plan_for_animals(plan, animals, auth.farm_id)
        if count == 0:
            return rx.toast.info(
                "Nothing recorded — plan feeds may be missing from your feed types."
            )
        return rx.toast.success(
            f"Fed {len(animals)} {plan['category']}(s) · {count} entries recorded."
        )

    # ── Dashboard cards ───────────────────────────────────────────────

    @rx.var
    def feed_remaining_total(self) -> float:
        return round(sum(s["quantity"] for s in self.inventory), 1)

    @rx.var
    def low_stock_count(self) -> int:
        return sum(1 for s in self.inventory if s["quantity"] <= 10)

    @rx.var
    async def today_ai_recommendation(self) -> dict:
        recs = await self.ai_recommendations
        return recs[0] if recs else {}

    @rx.var
    async def dashboard_cards(self) -> list[dict]:
        cost_per_liter = await self.feed_cost_per_liter
        best = await self.best_performing_cow
        ranks = await self.efficiency_ranks
        avg_score = round(sum(r["score"] for r in ranks) / len(ranks), 1) if ranks else 0
        rec = await self.today_ai_recommendation
        return [
            {"icon": "🌾", "title": "Feed Remaining", "value": f"{self.feed_remaining_total} units", "sub": "across all feed types", "color": "text-blue-600 bg-blue-50"},
            {"icon": "🥛", "title": "Feed Cost / Liter", "value": f"₹{cost_per_liter:.2f}", "sub": "this month", "color": "text-emerald-600 bg-emerald-50"},
            {"icon": "🐄", "title": "Best Performer", "value": best.get("name", "—"), "sub": f"{best.get('score', 0)} · {best.get('rank', '')}", "color": "text-amber-600 bg-amber-50"},
            {"icon": "📈", "title": "Feed Efficiency", "value": f"{avg_score}/100", "sub": "average score", "color": "text-purple-600 bg-purple-50"},
            {"icon": "⚠️", "title": "Feed Running Low", "value": str(self.low_stock_count), "sub": "stock items ≤10 units", "color": "text-red-600 bg-red-50"},
            {"icon": "🤖", "title": "Today's AI Advice", "value": rec.get("title", "—"), "sub": rec.get("action", "Add feeding data for advice"), "color": "text-teal-600 bg-teal-50"},
        ]

    # ── Feed reports (PDF export) ─────────────────────────────────────

    def _report_lines(
        self,
        report_type: str,
        cattle_list: list[dict],
        transactions: list[dict],
        recommendations: list[dict],
    ) -> list[str]:
        """Build plain-text lines for a feed report from real data."""
        ft_map = self._feed_type_map()
        today = datetime.date.today()
        month_start = today.replace(day=1).isoformat()
        consumption_cost = sum(
            c["quantity"] * ft_map.get(c["feed_type_id"], {}).get("cost_per_unit", 0)
            for c in self._consumptions_in_range(30)
        )
        purchase_cost = sum(
            float(t["amount"])
            for t in transactions
            if t["type"] == "expense"
            and t["category"]["name"] == "Cattle Feed"
            and t["date"] >= month_start
        )
        total_cost = consumption_cost + purchase_cost
        milk_liters = sum(
            float(r.get("liters", 0))
            for c in cattle_list
            for r in c.get("milk_production", [])
            if r["date"] >= (today - datetime.timedelta(days=30)).isoformat()
        )
        lines = []

        if report_type == "daily":
            todays = [c for c in self.consumptions if c["date"] == today.isoformat()]
            if not todays:
                lines.append("No feeding recorded today.")
            for c in sorted(todays, key=lambda x: (x["time_of_day"], x["animal_name"])):
                lines.append(
                    f"  {c['time_of_day']} | {c['animal_name']} | {c['feed_name']} | "
                    f"{c['quantity']} {c['unit']} | {c['notes'] or '-'}"
                )
            total = sum(c["quantity"] for c in todays)
            units = {c["unit"] for c in todays}
            lines.append(f"  TOTAL recorded today: {total} ({', '.join(units) or 'units'})")

        elif report_type == "monthly_cost":
            lines.append(f"Consumption cost (30d): Rs {consumption_cost:,.2f}")
            lines.append(f"Feed purchase expenses this month: Rs {purchase_cost:,.2f}")
            lines.append(f"Total feed cost: Rs {total_cost:,.2f}")
            lines.append(f"Milk produced (30d): {milk_liters:.1f} L")
            if milk_liters > 0:
                lines.append(f"Feed cost per liter: Rs {total_cost / milk_liters:.2f}")
            else:
                lines.append("Feed cost per liter: n/a (no milk recorded)")
            lines.append("")
            lines.append("Per feed type (30d consumption):")
            for item in self.consumption_by_feed:
                lines.append(f"  {item['name']}: {item['qty']} kg, Rs {item['cost']:,.2f}")

        elif report_type == "milk_feed":
            lines.append("Milk L/day (7d avg) | Feed kg/7d | Feed Rs/7d")
            for c in cattle_list:
                milk = self._animal_avg_milk(c, 7)
                kg = self._animal_feed_kg(c["id"], 7)
                cost = self._animal_feed_cost(c["id"], 7)
                lines.append(f"  {c['name']}: {milk:.1f} | {kg:.1f} | Rs {cost:.2f}")

        elif report_type == "purchase":
            for s in self.purchase_suggestions:
                lines.append(
                    f"  {s['name']}: {s['remaining']} {s['unit']} left, ~{s['days_left']} days. "
                    f"Buy {s['buy_qty']} {s['unit']}."
                )
            if not self.purchase_suggestions:
                lines.append("No purchase suggestions yet — record feeding first.")

        elif report_type == "waste":
            flagged = 0
            for c in cattle_list:
                kg = self._animal_feed_kg(c["id"], 7)
                milk = self._animal_avg_milk(c, 7)
                if kg > 0 and milk > 0 and (milk / kg) < 0.3:
                    flagged += 1
                    lines.append(
                        f"  {c['name']}: {kg:.1f} kg feed / {milk:.1f} L milk — check for wastage."
                    )
            if flagged == 0:
                lines.append("No animals flagged for low feed conversion.")
            lines.append("")
            lines.append("Tip: reduce spillage, use feeders, feed smaller portions more often.")

        elif report_type == "nutrition":
            for c in cattle_list:
                milk = self._animal_avg_milk(c, 7)
                kg = self._animal_feed_kg(c["id"], 7)
                cost = self._animal_feed_cost(c["id"], 7)
                lines.append(f"  {c['name']}: {milk:.1f} L/day | {kg:.1f} kg feed/7d | Rs {cost:.2f}/7d")
            lines.append("")
            lines.append("Advisor recommendations:")
            for r in recommendations[:5]:
                lines.append(f"  [{r['title']}] {r['action']}")
            if not recommendations:
                lines.append("  No recommendations yet — add milk & feeding data.")

        return lines

    @rx.event
    async def generate_feed_report(self, report_type: str):
        """Generate a PDF feed report and trigger a download."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            cs = await self.get_state(CattleState)
            ts = await self.get_state(TransactionState)
            recs = await self.ai_recommendations
            lines = self._report_lines(
                report_type, cs.cattle_list, ts.transactions, recs
            )

            filename = (
                f"feed_{report_type}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            )
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / filename
            c = canvas.Canvas(file_path, pagesize=letter)
            y = 750
            c.drawString(100, y, "AgriLedger - Feed Intelligence Report")
            y -= 20
            title = report_type.replace("_", " ").title()
            c.drawString(
                100, y, f"{title}  |  Generated {datetime.date.today().isoformat()}"
            )
            y -= 30
            for line in lines:
                if y < 50:
                    c.showPage()
                    y = 750
                c.drawString(100, y, line[:110])
                y -= 15
            c.save()
            self.generated_report_url = f"/_upload/{filename}"
            return rx.download(url=self.generated_report_url, filename=filename)
        except Exception as e:
            logging.exception(f"Error generating feed report: {e}")
            return rx.toast.error(f"Could not generate report: {e}")

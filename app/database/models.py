"""AgriLedger database models.

Defines TypedDict models for all data structures in the application.
"""

from typing import Literal, Optional, TypedDict

# ─── Enums / Literal Types ────────────────────────────────────────────

ActivityType = Literal[
    "Planting",
    "Fertilizing",
    "Pesticide Application",
    "Irrigation",
    "Weeding",
    "Harvesting",
    "Expense",
]
CropStatus = Literal["Planted", "Growing", "Harvested", "Fallow"]
BreedingCattleType = Literal["cow", "buffalo"]
CalfSex = Literal["male", "female"]
BreedingStatus = Literal["pending_confirmation", "pregnant", "calved", "not_pregnant"]
CalvingOutcome = Literal["live_birth", "stillbirth", "aborted"]
CattleHealthStatus = Literal["Healthy", "Sick", "Under Treatment", "Vaccinated"]
AnimalType = Literal["cow", "bull", "buffalo", "sheep", "goat", "hen", "cock", "chick"]
TransactionType = Literal["income", "expense"]
UserRole = Literal["admin", "worker", "viewer", "user"]
Severity = Literal["Normal", "Attention Needed", "Critical"]


# ─── User Models ──────────────────────────────────────────────────────

class User(TypedDict):
    name: str
    email: str
    password: str
    role: UserRole
    farm_id: Optional[str]
    phone: Optional[str]
    is_active: bool


class ActivityLog(TypedDict):
    id: str
    user_email: str
    action: str
    entity_type: str
    entity_id: Optional[str]
    details: Optional[str]
    timestamp: str
    ip_address: Optional[str]


# ─── Cattle Models ────────────────────────────────────────────────────

class MilkProduction(TypedDict):
    date: str
    liters: float
    notes: Optional[str]


class VaccinationRecord(TypedDict):
    date: str
    vaccine_name: str
    veterinarian: str
    next_due_date: Optional[str]
    notes: Optional[str]


class HealthNote(TypedDict):
    date: str
    note: str
    severity: Severity


class FeedRecord(TypedDict):
    date: str
    feed_type: str
    quantity_kg: float
    cost: float
    notes: Optional[str]


class Cattle(TypedDict):
    id: str
    name: str
    animal_type: AnimalType
    tag_number: str
    age: int
    breed: str
    purchase_date: str
    purchase_price: float
    image_url: str
    health_status: CattleHealthStatus
    milk_production: list[MilkProduction]
    vaccinations: list[VaccinationRecord]
    health_notes: list[HealthNote]
    feed_records: list[FeedRecord]
    is_juvenile: bool
    parent_id: Optional[str]
    mother_id: Optional[str]
    weight: Optional[float]
    is_active: bool


# ─── Crop Models ──────────────────────────────────────────────────────

class CropActivity(TypedDict):
    id: str
    date: str
    activity_type: ActivityType
    notes: str
    cost: float


class HarvestRecord(TypedDict):
    id: str
    date: str
    quantity: float
    unit: str
    income: float


class Crop(TypedDict):
    id: str
    name: str
    field_name: str
    planting_date: str
    status: CropStatus
    image_url: str
    activities: list[CropActivity]
    harvests: list[HarvestRecord]


# ─── Transaction Models ──────────────────────────────────────────────

class Category(TypedDict):
    name: str
    icon: str


class Transaction(TypedDict):
    type: TransactionType
    category: Category
    amount: float
    date: str
    notes: str


class CoconutSale(TypedDict):
    id: str
    date: str
    coconut_count: int
    price_per_coconut: float
    total_amount: float
    buyer: Optional[str]
    notes: Optional[str]


class MilkSale(TypedDict):
    id: str
    date: str
    animal_id: Optional[str]
    liters: float
    fat_percentage: float
    snf_percentage: float
    clr: Optional[float]
    water_ratio: Optional[float]
    rate_per_liter: float
    total_price: float
    buyer: Optional[str]
    bill_number: Optional[str]
    payment_status: str  # "pending" | "paid"
    paid_date: Optional[str]
    notes: Optional[str]


class MilkSocietyRateSlab(TypedDict):
    fat_min: float
    rate: float


class MilkSocietyRate(TypedDict):
    farm_id: str
    society: str
    slabs: list[MilkSocietyRateSlab]


# ─── Feed Models ──────────────────────────────────────────────────────

FeedCategory = Literal["Concentrate", "Home Grown"]
FeedUnit = Literal["kg", "bundles", "bags"]
StockStatus = Literal["Sufficient", "Low", "Out of Stock"]
TimeOfDay = Literal["Morning", "Evening"]
PlanCategory = Literal[
    "Calf", "Heifer", "Pregnant Cow", "Lactating Cow", "Dry Cow", "Bull"
]


class FeedType(TypedDict):
    id: str
    name: str
    category: FeedCategory
    unit: FeedUnit
    cost_per_unit: float
    is_custom: bool
    farm_id: str


class FeedStock(TypedDict):
    id: str
    feed_type_id: str
    feed_name: str
    quantity: float
    unit: FeedUnit
    purchase_date: str
    supplier: str
    cost: float
    expiry_date: Optional[str]
    farm_id: str


class FeedConsumption(TypedDict):
    id: str
    date: str
    time_of_day: TimeOfDay
    animal_id: str
    animal_name: str
    feed_type_id: str
    feed_name: str
    quantity: float
    unit: FeedUnit
    notes: str
    farm_id: str


class PlanFeedItem(TypedDict):
    feed_type_id: str
    feed_name: str
    quantity: float
    unit: FeedUnit


class FeedingPlan(TypedDict):
    id: str
    category: PlanCategory
    name: str
    morning: list[PlanFeedItem]
    evening: list[PlanFeedItem]
    minerals: str
    water_reminder: bool
    farm_id: str


# ─── Breeding Models ─────────────────────────────────────────────────

class FollowUpCheck(TypedDict):
    date: str
    notes: str


class BreedingCycle(TypedDict):
    id: str
    cattle_id: str
    cattle_name: str
    cattle_type: BreedingCattleType
    hormone_injection_date: str
    insemination_date: str
    pregnancy_confirmed: bool
    pregnancy_confirmation_date: Optional[str]
    expected_calving_date: str
    follow_up_checks: list[FollowUpCheck]
    repeat_breeding_indicator: bool
    calf_born: bool
    calf_sex: Optional[CalfSex]
    calf_health: Optional[str]
    birth_outcome: Optional[CalvingOutcome]
    notes: Optional[str]
    status: BreedingStatus
    created_date: str

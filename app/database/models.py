from typing import TypedDict, Literal, Optional

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
AnimalType = Literal["cow", "buffalo", "sheep", "goat", "hen", "cock", "chick"]
TransactionType = Literal["income", "expense"]


class User(TypedDict):
    name: str
    email: str
    password: str
    role: Optional[str]
    farm_id: Optional[str]


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
    severity: Literal["Normal", "Attention Needed", "Critical"]


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
    is_juvenile: bool
    parent_id: Optional[str]
    mother_id: Optional[str]
    weight: Optional[float]
    is_active: bool


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
    water_ratio: Optional[float]
    rate_per_liter: float
    total_price: float
    buyer: Optional[str]
    notes: Optional[str]


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
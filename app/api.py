"""AgriLedger REST API.

Mounted inside the Reflex server via ``rx.App(api_transformer=...)`` so a
single process/port serves the UI, websockets, and this API. Field names here
mirror ``app/database/models.py`` exactly, so rows created through the API are
indistinguishable from rows created through the UI.
"""

import re
import uuid
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.config import config
from app.database import crud
from app.database.connection import ensure_indexes_once, get_db, ping_db
from app.middleware.rate_limiter import RateLimitMiddleware, SecurityHeadersMiddleware
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

APP_VERSION = "1.0.0"

app = FastAPI(
    title="AgriLedger API",
    version=APP_VERSION,
    description="REST API for the AgriLedger smart farming platform.",
)

# Compression: JSON payloads and docs shrink 3–10x over slow rural links.
# Passes websocket scopes through untouched (verified in this Starlette).
app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=6)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS setup for frontend integration (explicit origins, never "*" with credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(config.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (Reflex infrastructure paths are exempt)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=config.rate_limit_max_requests,
    window_seconds=config.rate_limit_window_seconds,
)

bearer_scheme = HTTPBearer(auto_error=False)
EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")


def _validate_email(email: str) -> None:
    if not EMAIL_RE.fullmatch(email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email format.",
        )


# ─── Pydantic Schemas ──────────────────────────────────────────────────


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)


class UserOut(BaseModel):
    name: str
    email: str
    role: str
    farm_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class HealthResponse(BaseModel):
    status: str
    database: str
    environment: str
    version: str


# Field names mirror app/database/models.py so API rows == UI rows.
class CattleCreate(BaseModel):
    name: str
    animal_type: str = "cow"
    tag_number: str
    age: int = Field(..., ge=0)
    breed: str = ""
    purchase_date: str = ""
    purchase_price: float = Field(0.0, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    health_status: str = "Healthy"
    is_juvenile: bool = False


class CropCreate(BaseModel):
    name: str
    field_name: str = "Main Field"
    planting_date: str
    status: str = "Planted"
    initial_cost: float = Field(0.0, ge=0)


class TransactionCreate(BaseModel):
    type: str  # "income" | "expense"
    category: str
    amount: float = Field(..., gt=0)
    date: str
    notes: str = ""


class MilkSaleCreate(BaseModel):
    date: str
    liters: float = Field(..., gt=0)
    fat_percentage: float = Field(4.0, ge=0, le=100)
    snf_percentage: float = Field(8.5, ge=0, le=100)
    rate_per_liter: float = Field(..., ge=0)
    animal_id: Optional[str] = None
    buyer: Optional[str] = None
    bill_number: Optional[str] = None
    payment_status: str = "pending"
    notes: Optional[str] = None


# ─── Auth Dependencies ─────────────────────────────────────────────────


async def get_current_user_email(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """Resolve the caller's email from a valid bearer token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email = decode_access_token(credentials.credentials)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return email


async def get_current_user(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    """Resolve the full user document."""
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User account not found."
        )
    return user


# ─── Health Endpoints ──────────────────────────────────────────────────


@app.get("/health", response_model=HealthResponse)
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """System health check; creates DB indexes once before real traffic."""
    await ensure_indexes_once()
    db_connected = await ping_db()
    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        database="connected" if db_connected else "disconnected",
        environment=config.env,
        version=APP_VERSION,
    )


# ─── Auth & User Endpoints ─────────────────────────────────────────────


@app.post("/users/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    _validate_email(user.email)
    email = user.email.strip().lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    new_user = {
        "name": user.name.strip(),
        "email": email,
        "password": hash_password(user.password),
        "role": "viewer",
        "farm_id": str(uuid.uuid4()),
        "phone": None,
        "is_active": True,
    }
    await db.users.insert_one(new_user)
    return UserOut(
        name=new_user["name"],
        email=new_user["email"],
        role=new_user["role"],
        farm_id=new_user["farm_id"],
    )


@app.post("/auth/token")
async def login(creds: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    _validate_email(creds.email)
    user = await db.users.find_one({"email": creds.email.strip().lower()})
    if not user or not verify_password(creds.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    return {
        "access_token": create_access_token(user["email"]),
        "token_type": "bearer",
        "email": user["email"],
        "farm_id": user.get("farm_id", ""),
    }


@app.get("/users/{email}", response_model=UserOut)
async def get_user(
    email: str,
    current_email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_email != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this profile.",
        )
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return UserOut(
        name=user["name"],
        email=user["email"],
        role=user.get("role", "viewer"),
        farm_id=user.get("farm_id"),
    )


# ─── Cattle Endpoints ──────────────────────────────────────────────────


@app.get("/api/cattle")
async def list_cattle(current_user: dict = Depends(get_current_user)):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    return await crud.get_all_cattle(farm_id)


@app.post("/api/cattle", status_code=status.HTTP_201_CREATED)
async def add_cattle(
    data: CattleCreate, current_user: dict = Depends(get_current_user)
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    cattle_doc = {
        "id": str(uuid.uuid4()),
        "farm_id": farm_id,
        "name": data.name,
        "animal_type": data.animal_type,
        "tag_number": data.tag_number,
        "age": data.age,
        "breed": data.breed,
        "purchase_date": data.purchase_date,
        "purchase_price": data.purchase_price,
        "image_url": f"https://api.dicebear.com/9.x/notionists/svg?seed={data.name}",
        "health_status": data.health_status,
        "milk_production": [],
        "vaccinations": [],
        "health_notes": [],
        "feed_records": [],
        "is_juvenile": data.is_juvenile,
        "parent_id": None,
        "mother_id": None,
        "weight": data.weight,
        "is_active": True,
    }
    success = await crud.create_cattle(cattle_doc)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save animal record.",
        )
    return cattle_doc


# ─── Crop Endpoints ────────────────────────────────────────────────────


@app.get("/api/crops")
async def list_crops(current_user: dict = Depends(get_current_user)):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    return await crud.get_all_crops(farm_id)


@app.post("/api/crops", status_code=status.HTTP_201_CREATED)
async def add_crop(
    data: CropCreate, current_user: dict = Depends(get_current_user)
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    crop_doc = {
        "id": str(uuid.uuid4()),
        "farm_id": farm_id,
        "name": data.name,
        "field_name": data.field_name,
        "planting_date": data.planting_date,
        "status": data.status,
        "image_url": f"https://api.dicebear.com/9.x/shapes/svg?seed={data.name}",
        "activities": (
            [
                {
                    "id": str(uuid.uuid4()),
                    "date": data.planting_date,
                    "activity_type": "Planting",
                    "notes": "Initial planting.",
                    "cost": data.initial_cost,
                }
            ]
            if data.initial_cost > 0
            else []
        ),
        "harvests": [],
    }
    success = await crud.create_crop(crop_doc)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save crop record.",
        )
    return crop_doc


# ─── Transaction Endpoints ─────────────────────────────────────────────


@app.get("/api/transactions")
async def list_transactions(
    type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    transactions = await crud.get_all_transactions(farm_id)
    if type:
        transactions = [t for t in transactions if t.get("type") == type]
    return transactions


@app.post("/api/transactions", status_code=status.HTTP_201_CREATED)
async def add_transaction(
    data: TransactionCreate, current_user: dict = Depends(get_current_user)
):
    if data.type not in ("income", "expense"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Type must be 'income' or 'expense'.",
        )
    farm_id = current_user.get("farm_id") or current_user.get("email")
    tx_doc = {
        "type": data.type,
        "category": {"name": data.category, "icon": "ellipsis"},
        "amount": data.amount,
        "date": data.date,
        "notes": data.notes,
        "farm_id": farm_id,
        "id": str(uuid.uuid4()),
    }
    success = await crud.create_transaction(tx_doc)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save transaction.",
        )
    return tx_doc


# ─── Milk Sale Endpoints ───────────────────────────────────────────────


@app.get("/api/milk-sales")
async def list_milk_sales(current_user: dict = Depends(get_current_user)):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    return await crud.get_all_milk_sales(farm_id)


@app.post("/api/milk-sales", status_code=status.HTTP_201_CREATED)
async def add_milk_sale(
    data: MilkSaleCreate, current_user: dict = Depends(get_current_user)
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    sale_doc = {
        "id": str(uuid.uuid4()),
        "farm_id": farm_id,
        "date": data.date,
        "animal_id": data.animal_id,
        "liters": data.liters,
        "fat_percentage": data.fat_percentage,
        "snf_percentage": data.snf_percentage,
        "clr": None,
        "water_ratio": None,
        "rate_per_liter": data.rate_per_liter,
        "total_price": round(data.liters * data.rate_per_liter, 2),
        "buyer": data.buyer,
        "bill_number": data.bill_number,
        "payment_status": data.payment_status,
        "paid_date": data.date if data.payment_status == "paid" else None,
        "notes": data.notes,
    }
    success = await crud.create_milk_sale(sale_doc)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save milk sale record.",
        )
    return sale_doc


# ─── Summary Analytics Endpoint ────────────────────────────────────────


@app.get("/api/summary")
async def get_summary(current_user: dict = Depends(get_current_user)):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    cattle = await crud.get_all_cattle(farm_id)
    crops = await crud.get_all_crops(farm_id)
    transactions = await crud.get_all_transactions(farm_id)
    milk_sales = await crud.get_all_milk_sales(farm_id)

    total_income = sum(
        float(t.get("amount", 0) or 0) for t in transactions if t.get("type") == "income"
    )
    total_expenses = sum(
        float(t.get("amount", 0) or 0)
        for t in transactions
        if t.get("type") == "expense"
    )
    total_milk_liters = sum(float(s.get("liters", 0) or 0) for s in milk_sales)

    return {
        "farm_id": farm_id,
        "animals_count": len(cattle),
        "crops_count": len(crops),
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(total_income - total_expenses, 2),
        "total_milk_liters": round(total_milk_liters, 2),
    }


# ─── Coconut Sales Endpoints ──────────────────────────────────────────


class CoconutSaleCreate(BaseModel):
    date: str
    coconut_count: int = Field(..., gt=0)
    price_per_coconut: float = Field(..., gt=0)
    buyer: Optional[str] = None
    notes: Optional[str] = None


@app.get("/api/coconut-sales")
async def list_coconut_sales(current_user: dict = Depends(get_current_user)):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    return await crud.get_all_coconut_sales(farm_id)


@app.post("/api/coconut-sales", status_code=status.HTTP_201_CREATED)
async def add_coconut_sale(
    data: CoconutSaleCreate, current_user: dict = Depends(get_current_user)
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    total_amount = round(data.coconut_count * data.price_per_coconut, 2)
    sale_doc = {
        "id": str(uuid.uuid4()),
        "farm_id": farm_id,
        "date": data.date,
        "coconut_count": data.coconut_count,
        "price_per_coconut": data.price_per_coconut,
        "total_amount": total_amount,
        "buyer": data.buyer,
        "notes": data.notes,
    }
    success = await crud.create_coconut_sale(sale_doc)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save coconut sale record.",
        )

    # Also record auto income transaction
    tx_doc = {
        "id": str(uuid.uuid4()),
        "farm_id": farm_id,
        "type": "income",
        "category": {"name": "Coconut Sales", "icon": "coconut"},
        "amount": total_amount,
        "date": data.date,
        "notes": f"Coconut sale: {data.coconut_count} pcs @ ₹{data.price_per_coconut}",
    }
    await crud.create_transaction(tx_doc)

    return sale_doc


# ─── Breeding Endpoints ────────────────────────────────────────────────


class BreedingCreate(BaseModel):
    cattle_id: str
    cattle_name: str
    cattle_type: str = "cow"
    hormone_injection_date: str
    insemination_date: str
    pregnancy_confirmed: bool = False
    expected_calving_date: str = ""
    status: str = "pending_confirmation"
    notes: Optional[str] = None


@app.get("/api/breeding")
async def list_breeding_cycles(current_user: dict = Depends(get_current_user)):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    return await crud.get_all_breeding_cycles(farm_id)


@app.post("/api/breeding", status_code=status.HTTP_201_CREATED)
async def add_breeding_cycle(
    data: BreedingCreate, current_user: dict = Depends(get_current_user)
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    # Auto calculate expected calving date if not provided
    from datetime import datetime, timedelta
    exp_date = data.expected_calving_date
    if not exp_date and data.insemination_date:
        try:
            ins_dt = datetime.strptime(data.insemination_date, "%Y-%m-%d")
            days = 310 if data.cattle_type == "buffalo" else 283
            exp_date = (ins_dt + timedelta(days=days)).strftime("%Y-%m-%d")
        except Exception:
            exp_date = ""

    cycle_doc = {
        "id": str(uuid.uuid4()),
        "farm_id": farm_id,
        "cattle_id": data.cattle_id,
        "cattle_name": data.cattle_name,
        "cattle_type": data.cattle_type,
        "hormone_injection_date": data.hormone_injection_date,
        "insemination_date": data.insemination_date,
        "pregnancy_confirmed": data.pregnancy_confirmed,
        "pregnancy_confirmation_date": (
            data.insemination_date if data.pregnancy_confirmed else None
        ),
        "expected_calving_date": exp_date,
        "follow_up_checks": [],
        "repeat_breeding_indicator": False,
        "calf_born": False,
        "calf_sex": None,
        "calf_health": None,
        "birth_outcome": None,
        "notes": data.notes,
        "status": data.status,
        "created_date": data.insemination_date,
    }
    success = await crud.create_breeding_cycle(cycle_doc)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save breeding cycle record.",
        )
    return cycle_doc


@app.put("/api/breeding/{cycle_id}")
async def update_breeding_cycle_endpoint(
    cycle_id: str, updates: dict, current_user: dict = Depends(get_current_user)
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    success = await crud.update_breeding_cycle(cycle_id, updates, farm_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Breeding cycle not found or update failed.",
        )
    return {"status": "success", "id": cycle_id}


# ─── Weather Endpoint ──────────────────────────────────────────────────


@app.get("/api/weather")
async def get_weather(
    lat: float = 11.0168, lon: float = 76.9558
):
    """Fetch live forecast from Open-Meteo API."""
    import httpx
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
            f"&hourly=temperature_2m,relativehumidity_2m,precipitation_probability"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        )
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                data = res.json()
                current = data.get("current_weather", {})
                temp = current.get("temperature", 28.0)
                wind = current.get("windspeed", 12.0)
                weathercode = current.get("weathercode", 0)

                # Determine condition
                if weathercode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                    condition = "Rainy"
                    alert = "Rain forecast: hold pesticide spraying today."
                elif temp > 35:
                    condition = "Hot"
                    alert = "Heat stress warning: ensure extra drinking water for livestock."
                else:
                    condition = "Clear / Fair"
                    alert = "Optimal weather conditions for field activities."

                return {
                    "temperature": temp,
                    "windspeed": wind,
                    "condition": condition,
                    "alert": alert,
                    "daily": data.get("daily", {}),
                    "location": "Farm Region",
                }
    except Exception:
        pass

    # Safe fallback
    return {
        "temperature": 29.5,
        "windspeed": 10.0,
        "condition": "Partly Cloudy",
        "alert": "Good conditions for general farm operations.",
        "location": "Farm Region",
    }


# ─── AI Assistant Endpoints ─────────────────────────────────────────────


class AIChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


@app.post("/api/ai/chat")
async def ai_chat(
    data: AIChatRequest, current_user: dict = Depends(get_current_user)
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    cattle = await crud.get_all_cattle(farm_id)
    crops = await crud.get_all_crops(farm_id)
    transactions = await crud.get_all_transactions(farm_id)

    prompt = data.prompt.strip()

    # Try Gemini if API key configured
    if config.gemini_api_key:
        try:
            from app.services import gemini_service

            context = (
                f"You are AgriLedger AI, an intelligent farm management advisor. "
                f"Farm data: {len(cattle)} animals, {len(crops)} crops, {len(transactions)} transaction records. "
                f"User Question: {prompt}"
            )

            async def call_gemini(model_name: str):
                import google.generativeai as genai
                genai.configure(api_key=config.gemini_api_key)
                m = genai.GenerativeModel(model_name)
                res = await m.generate_content_async(context)
                return res.text if res else None

            ans = await gemini_service.retry_across_models(call_gemini)
            if ans:
                return {"answer": ans, "source": "Gemini AI"}
        except Exception:
            pass

    # Rule-based fallback
    lower = prompt.lower()
    if "milk" in lower or "yield" in lower:
        ans = f"Your farm currently manages {len(cattle)} registered animals. Ensure balanced concentrate feed and fresh green fodder to maximize daily milk yield."
    elif "profit" in lower or "income" in lower or "expense" in lower:
        inc = sum(float(t.get("amount", 0)) for t in transactions if t.get("type") == "income")
        exp = sum(float(t.get("amount", 0)) for t in transactions if t.get("type") == "expense")
        ans = f"Financial Snapshot: Total Income = ₹{inc:,.2f}, Total Expenses = ₹{exp:,.2f}, Net Profit = ₹{inc - exp:,.2f}."
    elif "crop" in lower or "field" in lower:
        ans = f"You have {len(crops)} crops planted. Check soil moisture and schedule weeding/fertilizing activities according to crop growth stage."
    else:
        ans = f"AgriLedger Assistant: For '{prompt}', we recommend monitoring key daily farm metrics, ensuring timely vaccinations, and keeping feed stock updated."

    return {"answer": ans, "source": "AgriLedger Smart Advisor"}


@app.get("/api/ai/health-score")
async def ai_health_score(current_user: dict = Depends(get_current_user)):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    cattle = await crud.get_all_cattle(farm_id)

    healthy_animals = sum(1 for c in cattle if c.get("health_status") == "Healthy")
    score = 85 if not cattle else int((healthy_animals / len(cattle)) * 100)

    recommendations = [
        "Schedule routine health checkups for lactating cattle.",
        "Ensure fodder silage is protected from excessive humidity.",
        "Review daily fat % and SNF metrics for optimal milk pricing.",
    ]

    return {
        "health_score": min(score, 98),
        "status": "Excellent" if score >= 80 else "Attention Needed",
        "recommendations": recommendations,
    }


# ─── Farm & Family Settings Endpoints ───────────────────────────────────


class FarmUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    location: str = ""
    size: str = ""


class FamilyMemberCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    phone: Optional[str] = None
    role: str = "member"


@app.get("/api/farm")
async def get_farm_settings(current_user: dict = Depends(get_current_user)):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    farm = await crud.get_farm(farm_id)
    if not farm:
        return {
            "farm_id": farm_id,
            "name": f"{current_user.get('name', 'My')}'s Farm",
            "location": "Coimbatore, Tamil Nadu",
            "size": "5 Acres",
        }
    return farm


@app.post("/api/farm")
async def update_farm_settings(
    data: FarmUpdate, current_user: dict = Depends(get_current_user)
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    settings = {"name": data.name, "location": data.location, "size": data.size}
    success = await crud.upsert_farm(farm_id, settings)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update farm settings.",
        )
    return {"status": "success", "farm_id": farm_id, **settings}


@app.get("/api/family")
async def list_family(current_user: dict = Depends(get_current_user)):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    return await crud.get_family_members(farm_id)


@app.post("/api/family", status_code=status.HTTP_201_CREATED)
async def add_family(
    data: FamilyMemberCreate, current_user: dict = Depends(get_current_user)
):
    from datetime import datetime as _datetime

    farm_id = current_user.get("farm_id") or current_user.get("email")
    _validate_email(data.email)
    member_doc = {
        "id": str(uuid.uuid4()),
        "farm_id": farm_id,
        "name": data.name,
        "email": data.email.strip().lower(),
        "phone": data.phone,
        "role": data.role,
        "status": "invited",
        "added_date": _datetime.now().strftime("%Y-%m-%d"),
    }
    success = await crud.create_family_member(member_doc)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save family member.",
        )
    return member_doc


@app.delete("/api/family/{member_id}")
async def remove_family_member(
    member_id: str, current_user: dict = Depends(get_current_user)
):
    farm_id = current_user.get("farm_id") or current_user.get("email")
    success = await crud.delete_family_member(farm_id, member_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found.",
        )
    return {"status": "deleted", "id": member_id}


# ─── Crop Disease Scanner Endpoints ────────────────────────────────────


class DiseaseScanRequest(BaseModel):
    crop_name: str
    symptoms: str
    observed_stage: str = "Growing"


@app.post("/api/disease-scanner/analyze")
async def analyze_crop_disease(data: DiseaseScanRequest):
    """Hybrid Agricultural Decision Engine for Crop Health & Treatments."""
    from app.services.hybrid_decision_engine import evaluate_hybrid_decision

    result = evaluate_hybrid_decision(
        crop_name=data.crop_name,
        symptoms=data.symptoms,
        observed_stage=data.observed_stage,
    )
    return result



from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
import os

app = FastAPI(title="AgriLedger API", version="1.0")

# CORS setup for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URI)
db = client["agriledger"]

# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"

class UserOut(BaseModel):
    name: str
    email: EmailStr
    role: str

@app.post("/users/register", response_model=UserOut)
async def register_user(user: UserCreate):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    await db.users.insert_one(user.dict())
    return UserOut(name=user.name, email=user.email, role=user.role)

@app.get("/users/{email}", response_model=UserOut)
async def get_user(email: EmailStr):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserOut(name=user["name"], email=user["email"], role=user.get("role", "user"))

# Add more endpoints for transactions, animals, crops, etc. as needed

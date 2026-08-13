import re
import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.config import config
from app.database.connection import get_db
from app.middleware.rate_limiter import RateLimitMiddleware
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

app = FastAPI(title="AgriLedger API", version="1.0")

# CORS setup for frontend integration (explicit origins, never "*" with credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(config.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    max_requests=config.rate_limit_max_requests,
    window_seconds=config.rate_limit_window_seconds,
)

db = get_db()

bearer_scheme = HTTPBearer(auto_error=False)


EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")


def _validate_email(email: str) -> None:
    if not EMAIL_RE.fullmatch(email):
        raise HTTPException(status_code=422, detail="Invalid email format.")


# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserOut(BaseModel):
    name: str
    email: str
    role: str


class LoginRequest(BaseModel):
    email: str
    password: str


def require_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Resolve the caller's email from a valid bearer token."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    email = decode_access_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return email


@app.post("/users/register", response_model=UserOut)
async def register_user(user: UserCreate):
    _validate_email(user.email)
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
        # Roles are assigned server-side; clients can never self-promote.
        "role": "viewer",
        "farm_id": str(uuid.uuid4()),
        "phone": None,
        "is_active": True,
    }
    await db.users.insert_one(new_user)
    return UserOut(name=user.name, email=user.email, role=new_user["role"])


@app.post("/auth/token")
async def login(creds: LoginRequest):
    _validate_email(creds.email)
    user = await db.users.find_one({"email": creds.email})
    if not user or not verify_password(creds.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    return {
        "access_token": create_access_token(creds.email),
        "token_type": "bearer",
        "email": creds.email,
    }


@app.get("/users/{email}", response_model=UserOut)
async def get_user(email: str, current_user: str = Depends(require_user)):
    # Users may only read their own profile.
    if current_user != email:
        raise HTTPException(status_code=403, detail="Not authorized to view this user.")
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserOut(
        name=user["name"], email=user["email"], role=user.get("role", "viewer")
    )


# Add more endpoints for transactions, animals, crops, etc. as needed

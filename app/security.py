"""Shared authentication helpers: password hashing and signed tokens.

Used by both the Reflex app (app/states/auth_state.py) and the FastAPI
API (app/api.py). bcrypt is required — there is no fallback; a missing
bcrypt fails fast at import time instead of silently downgrading.
"""

import base64
import hashlib
import hmac
import json
import time

import bcrypt

from app.config import config


def hash_password(password: str) -> str:
    """Hash a password with bcrypt (random salt per hash)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # Malformed hash (e.g. a legacy unsalted value) never matches.
        return False


def create_access_token(email: str, expires_seconds: int | None = None) -> str:
    """Return an HMAC-signed bearer token embedding the user's email."""
    seconds = expires_seconds if expires_seconds is not None else config.token_expiry_seconds
    payload = json.dumps(
        {"sub": email, "exp": int(time.time()) + seconds}, separators=(",", ":")
    ).encode("utf-8")
    body = base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")
    return f"{body}.{_sign(body)}"


def decode_access_token(token: str) -> str | None:
    """Return the email from a valid, unexpired token, else None."""
    try:
        body, signature = token.split(".", 1)
        if not hmac.compare_digest(signature, _sign(body)):
            return None
        payload = json.loads(
            base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)).decode("utf-8")
        )
        if int(payload.get("exp", 0)) < time.time():
            return None
        email = payload.get("sub")
        return email if isinstance(email, str) else None
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def _sign(body: str) -> str:
    digest = hmac.new(
        config.secret_key.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

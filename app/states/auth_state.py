import re
import time
import uuid

import reflex as rx

from app.database import crud
from app.database.models import User
from app.security import create_access_token, decode_access_token, hash_password, verify_password

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 900
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days of "stay signed in"
_failed_attempts: dict[str, list[float]] = {}


def _is_locked_out(email: str) -> bool:
    """True if the email has MAX_FAILED_ATTEMPTS failures within LOCKOUT_SECONDS."""
    now = time.time()
    attempts = [t for t in _failed_attempts.get(email, []) if now - t < LOCKOUT_SECONDS]
    _failed_attempts[email] = attempts
    return len(attempts) >= MAX_FAILED_ATTEMPTS


def _record_failure(email: str) -> None:
    _failed_attempts.setdefault(email, []).append(time.time())


def _clear_failures(email: str) -> None:
    _failed_attempts.pop(email, None)


def _sanitize_user(user: dict) -> User:
    """Project a DB user document onto the client-safe User shape.

    The password hash must never enter Reflex state: state vars used by the UI
    are serialized to the browser, so storing the full document there would
    leak the hash to every logged-in device.
    """
    return {
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "password": "",
        "role": user.get("role", "viewer"),
        "farm_id": user.get("farm_id"),
        "phone": user.get("phone"),
        "is_active": user.get("is_active", True),
    }


class AuthState(rx.State):
    """Manages authentication, user data, and registration/login forms.

    Sessions survive server restarts: the signed session token lives in a
    browser cookie, and ``current_user`` is rehydrated from the database on
    demand. ``current_user`` is always sanitized (no password hash).
    """

    # HMAC-signed token (email + expiry) persisted as a browser cookie.
    session_token: str = rx.Cookie(
        name="agriledger_session", max_age=SESSION_COOKIE_MAX_AGE, same_site="lax"
    )

    # Client-safe user projection (never contains the password hash).
    current_user: User | None = None

    error_message: str = ""
    is_loading: bool = False

    # ── Session helpers ─────────────────────────────────────────────────

    @rx.var
    def session_email(self) -> str:
        """Decode the signed cookie; empty string when absent/invalid/expired."""
        if not self.session_token:
            return ""
        return decode_access_token(self.session_token) or ""

    @rx.var
    def is_logged_in(self) -> bool:
        """True when the cookie carries a valid signed session."""
        return bool(self.session_email)

    @rx.event
    async def hydrate_user(self):
        """Load current_user from the DB if the session is valid but not loaded."""
        if self.current_user is not None:
            return
        email = self.session_email
        if not email:
            return
        user = await crud.get_user_by_email(email)
        if user and user.get("is_active", True):
            self.current_user = _sanitize_user(user)

    @rx.event
    def clear_errors(self):
        self.error_message = ""

    # ── Registration / login ────────────────────────────────────────────

    @rx.event
    async def register(self, form_data: dict):
        """Register a new user with password hashing."""
        self.error_message = ""
        name = str(form_data.get("name", "")).strip()
        email = str(form_data.get("email", "")).strip().lower()
        password = str(form_data.get("password", ""))
        confirm_password = str(form_data.get("confirm_password", ""))
        if not name:
            self.error_message = "Full name is required."
            return
        if not email:
            self.error_message = "Email is required."
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.error_message = "Enter a valid email address (e.g., name@example.com)."
            return
        if not password:
            self.error_message = "Password is required."
            return
        if len(password) < 8:
            self.error_message = "Password must be at least 8 characters long."
            return
        if not confirm_password:
            self.error_message = "Please confirm your password."
            return
        if password != confirm_password:
            self.error_message = "Passwords do not match. Please re-enter them."
            return
        existing_user = await crud.get_user_by_email(email)
        if existing_user:
            self.error_message = "User with this email already exists."
            return
        hashed_pw = hash_password(password)
        # If the farm owner added this email as a family member, the new
        # account joins that farm instead of creating a brand-new one.
        pending_invite = await crud.get_family_member_by_email(email)
        new_user: User = {
            "name": name,
            "email": email,
            "password": hashed_pw,
            "role": "viewer",
            "farm_id": (
                pending_invite["farm_id"] if pending_invite else str(uuid.uuid4())
            ),
            "phone": None,
            "is_active": True,
        }
        success = await crud.create_user(new_user)
        if not success:
            self.error_message = "Failed to create account. Please try again."
            return
        if pending_invite:
            await crud.update_family_member_status(pending_invite["id"], "active")
        self._start_session(new_user)
        return rx.redirect("/dashboard")

    @rx.event
    async def login(self, form_data: dict):
        """Log in an existing user with password verification."""
        self.error_message = ""
        email = str(form_data.get("email", "")).strip().lower()
        password = str(form_data.get("password", ""))
        if not email:
            self.error_message = "Email is required."
            return
        if not password:
            self.error_message = "Password is required."
            return
        user = await crud.get_user_by_email(email)
        if not user:
            self.error_message = "No account found with this email. Please sign up first."
            return
        if _is_locked_out(email):
            self.error_message = "Too many failed attempts. Try again in a few minutes."
            return
        if verify_password(password, user.get("password", "")):
            _clear_failures(email)
            self._start_session(user)
            return rx.redirect("/dashboard")
        _record_failure(email)
        self.error_message = "Incorrect password. Please try again."

    def _start_session(self, user: dict) -> None:
        """Persist a signed session cookie and cache the sanitized user."""
        self.session_token = create_access_token(user["email"])
        self.current_user = _sanitize_user(user)

    @rx.event
    async def logout(self):
        """Log out: clear the cookie and cached user, then go home."""
        self.reset()
        return rx.redirect("/")

    # ── Convenience accessors ───────────────────────────────────────────

    @rx.var
    def farm_id(self) -> str:
        """Returns the current user's farm_id, falling back to their email as unique key."""
        if self.current_user:
            return self.current_user.get("farm_id") or self.current_user.get("email", "")
        return ""

    @rx.var
    def user_name(self) -> str:
        """Returns the logged-in user's display name or a safe fallback."""
        if self.current_user and self.current_user.get("name"):
            return self.current_user["name"]
        return "Farmer"

    @rx.var
    def user_email(self) -> str:
        """Returns the logged-in user's email or empty string."""
        if self.current_user and self.current_user.get("email"):
            return self.current_user["email"]
        return ""

    @rx.event
    def update_current_user_name(self, name: str):
        """Update current_user's name in state after successful persistence."""
        if self.current_user:
            self.current_user = {**self.current_user, "name": name}

    @rx.event
    async def require_login(self):
        """Redirect to login if unauthenticated; else rehydrate the user."""
        if not self.is_logged_in:
            return rx.redirect("/login")
        await self.hydrate_user()

import re
import time
import uuid

import reflex as rx

from app.database import crud
from app.database.models import User
from app.security import hash_password, verify_password

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 900
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


class AuthState(rx.State):
    """Manages authentication, user data, and registration/login forms."""

    current_user: User | None = None
    is_logged_in: bool = False
    error_message: str = ""
    is_loading: bool = False

    @rx.event
    def clear_errors(self):
        self.error_message = ""

    @rx.event
    async def register(self, form_data: dict):
        """Register a new user with password hashing."""
        self.error_message = ""
        name = form_data.get("name", "").strip()
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        confirm_password = form_data.get("confirm_password", "")
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
        self.is_logged_in = True
        self.current_user = new_user
        return rx.redirect("/dashboard")

    @rx.event
    async def login(self, form_data: dict):
        """Log in an existing user with password verification."""
        self.error_message = ""
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
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
        stored_pw = user["password"]
        if _is_locked_out(email):
            self.error_message = "Too many failed attempts. Try again in a few minutes."
            return
        if verify_password(password, stored_pw):
            _clear_failures(email)
            self.is_logged_in = True
            self.current_user = user
            return rx.redirect("/dashboard")
        _record_failure(email)
        self.error_message = "Incorrect password. Please try again."

    @rx.event
    def logout(self):
        """Log out the current user."""
        self.is_logged_in = False
        self.current_user = None
        return rx.redirect("/")

    @rx.var
    def farm_id(self) -> str:
        """Returns the current user's farm_id, falling back to their email as unique key."""
        if self.current_user:
            return self.current_user.get("farm_id") or self.current_user.get("email", "")
        return ""

    @rx.event
    def require_login(self):
        """Redirect to login if user is not authenticated."""
        if not self.is_logged_in:
            return rx.redirect("/login")

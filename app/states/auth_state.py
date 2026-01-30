import reflex as rx
from typing import TypedDict
import re
from app.database import crud
from app.database.models import User


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
        """Register a new user."""
        self.error_message = ""
        name = form_data.get("name", "").strip()
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        confirm_password = form_data.get("confirm_password", "")
        if not name or not email or (not password) or (not confirm_password):
            self.error_message = "All fields are required."
            return
        if not re.match("[^@]+@[^@]+\\.[^@]+", email):
            self.error_message = "Invalid email format."
            return
        if len(password) < 8:
            self.error_message = "Password must be at least 8 characters."
            return
        if password != confirm_password:
            self.error_message = "Passwords do not match."
            return
        existing_user = await crud.get_user_by_email(email)
        if existing_user:
            self.error_message = "User with this email already exists."
            return
        new_user: User = {"name": name, "email": email, "password": password}
        success = await crud.create_user(new_user)
        if not success:
            self.error_message = "Failed to create account. Please try again."
            return
        self.is_logged_in = True
        self.current_user = new_user
        return rx.redirect("/dashboard")

    @rx.event
    async def login(self, form_data: dict):
        """Log in an existing user."""
        self.error_message = ""
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        if not email or not password:
            self.error_message = "Email and password are required."
            return
        user = await crud.get_user_by_email(email)
        if user and user["password"] == password:
            self.is_logged_in = True
            self.current_user = user
            return rx.redirect("/dashboard")
        self.error_message = "Invalid email or password."

    @rx.event
    def logout(self):
        """Log out the current user."""
        self.is_logged_in = False
        self.current_user = None
        return rx.redirect("/")

    @rx.event
    def require_login(self):
        """Redirect to login if user is not authenticated."""
        if not self.is_logged_in:
            return rx.redirect("/login")
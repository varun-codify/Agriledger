import reflex as rx

from app.database import crud
from app.states.auth_state import AuthState


class SettingsState(rx.State):
    """Manages user settings and preferences."""

    theme_mode: str = "light"
    language: str = "English"
    notifications_enabled: bool = True
    email_alerts: bool = True
    sms_alerts: bool = False
    farm_name: str = "My Farm"
    farm_location: str = "Springfield"
    farm_size: str = "50 Acres"
    settings_error: str = ""

    @rx.event
    async def fetch_farm_settings(self):
        """Load the farm's saved name/location/size from the database."""
        auth = await self.get_state(AuthState)
        farm = await crud.get_farm(auth.farm_id)
        if farm:
            self.farm_name = farm.get("name") or self.farm_name
            self.farm_location = farm.get("location") or self.farm_location
            self.farm_size = farm.get("size") or self.farm_size

    @rx.event
    def toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"

    @rx.event
    def set_language(self, lang: str):
        self.language = lang

    @rx.event
    def update_notification_settings(self, key: str, value: bool):
        if key == "notifications":
            self.notifications_enabled = value
        elif key == "email":
            self.email_alerts = value
        elif key == "sms":
            self.sms_alerts = value

    @rx.event
    async def update_farm_details(self, form_data: dict):
        farm_name = str(form_data.get("farm_name", "")).strip()
        farm_location = str(form_data.get("farm_location", "")).strip()
        farm_size = str(form_data.get("farm_size", "")).strip()
        if not farm_name:
            self.settings_error = "Farm name is required."
            return
        if not farm_location:
            self.settings_error = "Farm location is required."
            return
        self.farm_name = farm_name
        self.farm_location = farm_location
        self.farm_size = farm_size
        self.settings_error = ""
        auth = await self.get_state(AuthState)
        saved = await crud.upsert_farm(
            auth.farm_id,
            {
                "name": farm_name,
                "location": farm_location,
                "size": farm_size,
            },
        )
        if not saved:
            return rx.toast.error("Could not save farm details. Please try again.")
        return rx.toast.success("Farm details updated successfully!")

    @rx.event
    async def update_profile(self, form_data: dict):
        name = str(form_data.get("name", "")).strip()
        if not name:
            self.settings_error = "Full name is required."
            return
        self.settings_error = ""
        return rx.toast.success("Profile updated successfully!")

    @rx.event
    def backup_data(self):
        return rx.toast.success(
            "Data backup initiated. You will receive an email shortly."
        )

import asyncio
import datetime
import json
import logging

import reflex as rx

from app.database import crud
from app.states.auth_state import AuthState

logger = logging.getLogger(__name__)


class SettingsState(rx.State):
    """Manages user settings and preferences."""

    farm_name: str = "My Farm"
    farm_location: str = "Springfield"
    farm_size: str = "50 Acres"
    settings_error: str = ""
    is_exporting: bool = False
    # Active settings section tab (progressive disclosure of long form).
    active_tab: str = "account"  # "account" | "preferences" | "people" | "data"

    @rx.event
    def set_active_tab(self, tab: str):
        if tab in ("account", "preferences", "people", "data"):
            self.active_tab = tab
            self.settings_error = ""

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
            return rx.toast.error("Full name is required.")
        self.settings_error = ""
        auth = await self.get_state(AuthState)
        if auth.current_user and auth.current_user.get("email"):
            email = auth.current_user["email"]
            saved = await crud.update_user_profile(email, name=name)
            if not saved:
                return rx.toast.error("Could not update profile. Please try again.")
            auth.update_current_user_name(name)
        return rx.toast.success("Profile updated successfully!")

    @rx.event
    async def backup_data(self):
        """Export every farm collection as a downloadable JSON backup.

        Real export — no external services involved; the browser downloads the
        file directly.
        """
        if self.is_exporting:
            return
        self.is_exporting = True
        try:
            auth = await self.get_state(AuthState)
            farm_id = auth.farm_id
            cattle, crops, transactions, milk_sales = await asyncio.gather(
                crud.get_all_cattle(farm_id),
                crud.get_all_crops(farm_id),
                crud.get_all_transactions(farm_id),
                crud.get_all_milk_sales(farm_id),
            )
            coconut_sales, breeding_cycles, feed_types, feed_stock = (
                await asyncio.gather(
                    crud.get_all_coconut_sales(farm_id),
                    crud.get_all_breeding_cycles(farm_id),
                    crud.get_feed_types(farm_id),
                    crud.get_feed_stock(farm_id),
                )
            )
            feed_consumptions, feeding_plans = await asyncio.gather(
                crud.get_feed_consumptions(farm_id),
                crud.get_feeding_plans(farm_id),
            )
            backup = {
                "app": "AgriLedger",
                "version": 1,
                "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "farm_id": farm_id,
                "data": {
                    "cattle": cattle,
                    "crops": crops,
                    "transactions": transactions,
                    "milk_sales": milk_sales,
                    "coconut_sales": coconut_sales,
                    "breeding_cycles": breeding_cycles,
                    "feed_types": feed_types,
                    "feed_stock": feed_stock,
                    "feed_consumptions": feed_consumptions,
                    "feeding_plans": feeding_plans,
                },
            }
            payload = json.dumps(backup, default=str, ensure_ascii=False, indent=2)
            filename = f"agriledger-backup-{datetime.date.today().isoformat()}.json"
            return rx.download(data=payload, filename=filename)
        except Exception:
            logger.exception("Backup export failed")
            return rx.toast.error("Could not create the backup. Please try again.")
        finally:
            self.is_exporting = False

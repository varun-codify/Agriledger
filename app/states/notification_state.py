import reflex as rx

from app.states.auth_state import AuthState
from app.states.breeding_state import BreedingState
from app.states.cattle_state import CattleState
from app.states.dashboard_state import DashboardState


class NotificationState(rx.State):
    """Manages real-time in-app notifications and alerts."""

    notifications: list[dict] = []
    show_notifications: bool = False
    unread_count: int = 0
    loaded_once: bool = False

    @rx.event
    def toggle_notifications(self):
        self.show_notifications = not self.show_notifications

    @rx.event
    def close_notifications(self):
        self.show_notifications = False

    @rx.event
    def add_notification(self, notification: dict):
        """Add a new notification. notification should have: title, message, type, timestamp."""
        self.notifications.insert(0, notification)
        self.unread_count += 1

    @rx.event
    def mark_all_read(self):
        self.unread_count = 0

    @rx.event
    def clear_notifications(self):
        self.notifications = []
        self.unread_count = 0

    @rx.event
    def dismiss_notification(self, index: int):
        if 0 <= index < len(self.notifications):
            self.notifications.pop(index)
            if self.unread_count > 0:
                self.unread_count -= 1

    @rx.event
    async def load_notifications(self):
        """Build the notification list from live dashboard/breeding alerts.

        Runs once per session; subsequent visits keep whatever the user has
        dismissed so the panel doesn't refill on every navigation.
        """
        if self.loaded_once:
            return None
        auth = await self.get_state(AuthState)
        if not auth.is_logged_in:
            return None
        items: list[dict] = []
        try:
            dash = await self.get_state(DashboardState)
            reminders = await dash.reminders
            for r in reminders[:5]:
                if r.get("task") and "Add farm data" not in r["task"]:
                    items.append(
                        {
                            "title": "Reminder",
                            "message": r["task"],
                            "type": "reminder",
                            "timestamp": r.get("due", ""),
                        }
                    )
        except Exception:
            pass
        try:
            breeding = await self.get_state(BreedingState)
            checks = breeding.pregnancy_checks_due
            calvings = breeding.calvings_due_soon
            if checks:
                items.append(
                    {
                        "title": "Pregnancy checks due",
                        "message": f"{len(checks)} animal(s) need a pregnancy check.",
                        "type": "alert",
                        "timestamp": "",
                    }
                )
            if calvings:
                items.append(
                    {
                        "title": "Calving expected soon",
                        "message": f"{len(calvings)} animal(s) are close to calving.",
                        "type": "alert",
                        "timestamp": "",
                    }
                )
        except Exception:
            pass
        try:
            cattle = await self.get_state(CattleState)
            if cattle.cattle_list is not None and len(cattle.cattle_list) == 0:
                items.append(
                    {
                        "title": "Get started",
                        "message": "Add your first animal to start tracking your farm.",
                        "type": "info",
                        "timestamp": "",
                    }
                )
        except Exception:
            pass
        if items:
            self.notifications = items
            self.unread_count = len(items)
        self.loaded_once = True
        return None

import reflex as rx


class NotificationState(rx.State):
    """Manages real-time in-app notifications and alerts."""

    notifications: list[dict] = []
    show_notifications: bool = False
    unread_count: int = 0

    @rx.event
    def toggle_notifications(self):
        self.show_notifications = not self.show_notifications

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

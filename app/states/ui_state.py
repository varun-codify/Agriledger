import reflex as rx


class UIState(rx.State):
    """Handles the UI state of the application."""

    sidebar_collapsed: bool = False

    @rx.event
    def toggle_sidebar(self):
        """Toggles the sidebar's collapsed state."""
        self.sidebar_collapsed = not self.sidebar_collapsed
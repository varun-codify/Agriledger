import reflex as rx


class UIState(rx.State):
    """Handles the UI state of the application."""

    sidebar_collapsed: bool = False
    # Which sidebar accordion groups are expanded (by group name).
    sidebar_groups: dict[str, bool] = {
        "Farm": True,
        "Dairy & Sales": True,
        "Intelligence": True,
        "System": True,
    }
    # Active tab on the consolidated Insights & AI page.
    insights_tab: str = "weather"  # "weather" | "ai"
    # Dashboard content tabs (progressive disclosure — keeps the page scannable).
    dashboard_tab: str = "overview"  # "overview" | "analytics" | "production"
    # Mobile slide-in navigation drawer (shown below the md breakpoint).
    mobile_nav_open: bool = False
    # Whether the browser has a deferred install prompt ready to show
    # (set by ``check_install_status``, consumed by ``install_app``).
    install_prompt_available: bool = False
    # Dark mode (mirrors the ``dark`` class on <html>; persisted in localStorage).
    dark_mode: bool = False

    @rx.event
    def init_theme(self):
        """Sync ``dark_mode`` state with the class already applied by ag_patch.js."""
        return rx.call_script(
            "return document.documentElement.classList.contains('dark');",
            callback=UIState.set_dark_mode,
        )

    @rx.event
    def set_dark_mode(self, dark: bool):
        self.dark_mode = bool(dark)

    @rx.event
    def toggle_theme(self):
        """Flip dark/light mode and persist the choice in localStorage."""
        self.dark_mode = not self.dark_mode
        theme = "dark" if self.dark_mode else "light"
        return rx.call_script(
            f"""
            document.documentElement.classList.toggle('dark', {str(self.dark_mode).lower()});
            document.documentElement.classList.toggle('light', {str(not self.dark_mode).lower()});
            document.documentElement.style.colorScheme = '{theme}';
            try {{ localStorage.setItem('theme', '{theme}'); }} catch(e) {{}}
            """
        )

    @rx.event
    def toggle_sidebar(self):
        """Toggles the sidebar's collapsed state."""
        self.sidebar_collapsed = not self.sidebar_collapsed

    @rx.event
    def toggle_sidebar_group(self, group: str):
        """Expands or collapses a sidebar accordion group."""
        self.sidebar_groups[group] = not self.sidebar_groups.get(group, True)

    @rx.event
    def set_insights_tab(self, tab: str):
        """Switch between the weather and AI tabs on the Insights page."""
        if tab in ("weather", "ai"):
            self.insights_tab = tab

    @rx.event
    def set_dashboard_tab(self, tab: str):
        """Switch the Dashboard between Overview / Analytics / Production."""
        if tab in ("overview", "analytics", "production"):
            self.dashboard_tab = tab

    @rx.event
    def toggle_mobile_nav(self):
        """Opens or closes the mobile navigation drawer."""
        if self.mobile_nav_open:
            return self.close_mobile_nav()
        return self.open_mobile_nav()

    @rx.event
    def open_mobile_nav(self):
        """Opens the mobile drawer and locks background scrolling."""
        self.mobile_nav_open = True
        return rx.call_script("document.body.style.overflow = 'hidden'")

    @rx.event
    def close_mobile_nav(self):
        """Closes the mobile drawer and restores background scrolling."""
        self.mobile_nav_open = False
        return rx.call_script("document.body.style.overflow = ''")

    @rx.event
    def set_install_available(self, available: bool):
        """Callback for ``check_install_status`` — records prompt availability."""
        self.install_prompt_available = available

    @rx.event
    def check_install_status(self):
        """Ask the browser whether an install prompt is available.

        The script resolves with ``true`` once a deferred ``beforeinstallprompt``
        exists (or has been captured), ``false`` when the app is already installed
        or the browser will not offer one. Resolves within 10s at most so the
        listener is always cleaned up.
        """
        # Reuse a single pending check: this event fires on every dashboard page
        # mount, and stacking fresh window listeners + timers each time would be
        # wasteful. The shared promise is cleared when it settles, so a later
        # navigation can still pick up a newly captured prompt.
        return rx.call_script(
            "if (!window.__agriledgerInstallCheck) {"
            " window.__agriledgerInstallCheck = new Promise((resolve) => {"
            "  const installed = window.matchMedia &&"
            "   window.matchMedia('(display-mode: standalone)').matches;"
            "  if (installed) { window.__agriledgerInstallCheck = null; resolve(false); return; }"
            "  if (window.__agriledgerDeferredPrompt) {"
            "   window.__agriledgerInstallCheck = null; resolve(true); return;"
            "  }"
            "  const onPrompt = () => { cleanup(); resolve(true); };"
            "  const onInstalled = () => { cleanup(); resolve(false); };"
            "  const cleanup = () => {"
            "   window.__agriledgerInstallCheck = null;"
            "   window.removeEventListener('beforeinstallprompt', onPrompt);"
            "   window.removeEventListener('appinstalled', onInstalled);"
            "   clearTimeout(timer);"
            "  };"
            "  const timer = setTimeout(() => { cleanup(); resolve(false); }, 10000);"
            "  window.addEventListener('beforeinstallprompt', onPrompt);"
            "  window.addEventListener('appinstalled', onInstalled);"
            " });"
            "}"
            "return window.__agriledgerInstallCheck;",
            callback=UIState.set_install_available,
        )

    @rx.event
    def install_app(self):
        """Trigger the browser's install prompt from the in-app button.

        The deferred prompt is consumed in the process, so hide the button
        immediately (``beforeinstallprompt`` fires only once per session).
        """
        self.install_prompt_available = False
        return rx.call_script(
            "if (window.__agriledgerDeferredPrompt) {"
            " const p = window.__agriledgerDeferredPrompt;"
            " window.__agriledgerDeferredPrompt = null;"
            " p.prompt().catch(function() {});"
            "}"
        )

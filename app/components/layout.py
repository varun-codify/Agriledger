import reflex as rx

from app.components.common import install_app_button
from app.components.quick_add import quick_add_dialog
from app.states.auth_state import AuthState
from app.states.i18n_state import I18nState
from app.states.notification_state import NotificationState
from app.states.settings_state import SettingsState
from app.states.ui_state import UIState


def landing_header() -> rx.Component:
    """The header for the landing page."""
    return rx.el.header(
        rx.el.nav(
            # Logo/Brand
            rx.el.a(
                rx.el.div(
                    rx.icon(
                        "leaf",
                        class_name="h-7 w-7 text-emerald-500",
                        aria_hidden="true",
                    ),
                    rx.el.span(
                        "AgriLedger",
                        class_name="text-xl font-bold text-stone-800 hidden sm:inline dark:text-stone-100",
                    ),
                    class_name="flex items-center gap-2",
                ),
                href="/",
                aria_label="AgriLedger home page",
                class_name="focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded",
            ),
            # Desktop Navigation Links — hidden on phones; anchors remain in the footer.
            rx.el.div(
                rx.el.a(
                    "Features",
                    href="#features",
                    class_name="text-stone-600 hover:text-emerald-600 transition-colors font-medium dark:text-stone-300 dark:hover:text-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-3 py-2 min-h-[40px] flex items-center",
                    aria_label="View features",
                ),
                rx.el.a(
                    "About",
                    href="#about",
                    class_name="text-stone-600 hover:text-emerald-600 transition-colors font-medium dark:text-stone-300 dark:hover:text-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-3 py-2 min-h-[40px] flex items-center",
                    aria_label="Learn about us",
                ),
                rx.el.a(
                    "Pricing",
                    href="#pricing",
                    class_name="text-stone-600 hover:text-emerald-600 transition-colors font-medium dark:text-stone-300 dark:hover:text-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-3 py-2 min-h-[40px] flex items-center",
                    aria_label="View pricing plans",
                ),
                class_name="hidden md:flex items-center gap-4 lg:gap-8",
                role="navigation",
                aria_label="Primary navigation",
            ),
            # Auth Buttons — hide text links on very small screens (CTAs stay).
            rx.el.div(
                rx.el.button(
                    rx.icon(
                        rx.cond(UIState.dark_mode, "sun", "moon"),
                        class_name="h-4 w-4",
                    ),
                    on_click=UIState.toggle_theme,
                    aria_label="Toggle dark mode",
                    class_name="p-2.5 min-w-[40px] min-h-[40px] flex items-center justify-center rounded-lg text-stone-500 hover:bg-stone-100 hover:text-stone-700 transition-all active:scale-95 dark:text-stone-300 dark:hover:bg-stone-800",
                ),
                rx.el.a(
                    "Login",
                    href="/login",
                    class_name="hidden sm:inline-block text-stone-600 hover:text-emerald-600 font-medium dark:text-stone-300 dark:hover:text-emerald-400 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-3 py-2 min-h-[40px] flex items-center",
                    aria_label="Log in to your account",
                ),
                rx.el.a(
                    "Sign Up",
                    href="/register",
                    class_name="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-4 sm:px-5 py-2.5 min-h-[40px] rounded-lg hover:from-emerald-600 hover:to-emerald-700 font-semibold transition-all shadow-sm hover:shadow-md focus:outline-none focus:ring-4 focus:ring-emerald-300 active:scale-[0.98] flex items-center",
                    aria_label="Create new account",
                    role="button",
                ),
                class_name="flex items-center gap-2 sm:gap-4",
                role="group",
                aria_label="Authentication options",
            ),
            class_name="max-w-7xl mx-auto flex items-center justify-between gap-3 px-4 py-3",
            role="navigation",
            aria_label="Main navigation",
        ),
        class_name="bg-white/80 dark:bg-stone-950/80 backdrop-blur-md sticky top-0 z-50 border-b border-stone-200/50 dark:border-stone-800 shadow-sm",
        style={"scroll-behavior": "smooth"},
        role="banner",
    )


NAV_GROUPS = [
    {
        "name": "Farm",
        "name_key": "",
        "icon": "tractor",
        "items": [
            {"name": "Dashboard", "name_key": "nav.dashboard", "icon": "layout-dashboard", "href": "/dashboard"},
            {"name": "Animals", "name_key": "nav.animals", "icon": "git-fork", "href": "/cattle"},
            {"name": "Breeding Cycles", "name_key": "nav.breeding", "icon": "heart", "href": "/cattle/breeding"},
            {"name": "Crops", "name_key": "nav.crops", "icon": "sprout", "href": "/crops"},
        ],
    },
    {
        "name": "Dairy & Sales",
        "name_key": "",
        "icon": "droplets",
        "items": [
            {"name": "Milk & Bills", "name_key": "", "icon": "landmark", "href": "/milk"},
            {"name": "Transactions", "name_key": "", "icon": "arrow-left-right", "href": "/transactions"},
        ],
    },
    {
        "name": "Intelligence",
        "name_key": "",
        "icon": "brain-circuit",
        "items": [
            {"name": "Feed", "name_key": "", "icon": "wheat", "href": "/feed"},
            {"name": "Insights & AI", "name_key": "nav.insights", "icon": "bot", "href": "/insights"},
            {"name": "Crop Disease AI", "name_key": "", "icon": "scan-eye", "href": "/disease-scanner"},
        ],
    },
    {
        "name": "System",
        "name_key": "",
        "icon": "cog",
        "items": [
            {"name": "Reports", "name_key": "nav.reports", "icon": "file-text", "href": "/reports"},
            {"name": "Settings", "name_key": "nav.settings", "icon": "settings", "href": "/settings"},
        ],
    },
]

# Flat list used when the sidebar is collapsed to an icon-only rail.
ALL_NAV_ITEMS = [item for group in NAV_GROUPS for item in group["items"]]

# Primary destinations shown in the mobile bottom navigation bar.
MOBILE_BOTTOM_ITEMS = [
    {"name": "Home", "icon": "layout-dashboard", "href": "/dashboard"},
    {"name": "Animals", "icon": "git-fork", "href": "/cattle"},
    {"name": "Milk", "icon": "droplets", "href": "/milk"},
    {"name": "Feed", "icon": "wheat", "href": "/feed"},
]


def _nav_label(item: dict) -> rx.Var | str:
    """Translated nav label when a translation key exists; else the English name."""
    key = item.get("name_key") or ""
    if key:
        return I18nState.t[key]
    return item["name"]


def _is_active(href: str) -> rx.Var[bool]:
    """True when the current route is this nav item or one of its children."""
    path = rx.State.router.page.path
    if href == "/cattle":
        # /cattle/breeding (and its details) belong to the Breeding item.
        return (path == href) | (
            path.startswith("/cattle/") & ~path.startswith("/cattle/breeding")
        )
    return (path == href) | path.startswith(href + "/")


def sidebar_item(item: dict) -> rx.Component:
    """A single navigation item inside an accordion group."""
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5 flex-shrink-0"),
        rx.el.span(_nav_label(item), class_name="truncate"),
        href=item["href"],
        class_name=rx.cond(
            _is_active(item["href"]),
            "flex items-center gap-3 rounded-lg px-3 py-2.5 min-h-[40px] text-emerald-600 bg-emerald-50 transition-all dark:bg-emerald-950 dark:text-emerald-400",
            "flex items-center gap-3 rounded-lg px-3 py-2.5 min-h-[40px] text-stone-600 hover:bg-stone-100 transition-all dark:text-stone-300 dark:hover:bg-stone-800",
        ),
    )


def sidebar_icon_item(item: dict) -> rx.Component:
    """Icon-only link used when the sidebar is collapsed."""
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5"),
        href=item["href"],
        title=item["name"],
        aria_label=item["name"],
        class_name=rx.cond(
            _is_active(item["href"]),
            "flex items-center justify-center rounded-lg p-2.5 text-emerald-600 bg-emerald-50 transition-all dark:bg-emerald-950 dark:text-emerald-400",
            "flex items-center justify-center rounded-lg p-2.5 text-stone-600 hover:bg-stone-100 transition-all dark:text-stone-300 dark:hover:bg-stone-800",
        ),
    )


def sidebar_group_header(group: dict) -> rx.Component:
    """Collapsible header for one sidebar accordion group."""
    return rx.el.button(
        rx.icon(group["icon"], class_name="h-4 w-4 text-stone-400 flex-shrink-0"),
        rx.el.span(
            group["name"],
            class_name="text-[11px] font-bold uppercase tracking-wider text-stone-400 truncate",
        ),
        rx.icon(
            "chevron-down",
            class_name=rx.cond(
                UIState.sidebar_groups[group["name"]],
                "h-4 w-4 ml-auto text-stone-400 transition-transform duration-300",
                "h-4 w-4 ml-auto text-stone-400 transition-transform duration-300 -rotate-90",
            ),
        ),
        on_click=lambda: UIState.toggle_sidebar_group(group["name"]),
        class_name="flex w-full items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-stone-100 transition-colors dark:hover:bg-stone-800",
    )


def sidebar_group(group: dict) -> rx.Component:
    """One accordion group: header + collapsible item list."""
    return rx.el.div(
        sidebar_group_header(group),
        rx.cond(
            UIState.sidebar_groups[group["name"]],
            rx.el.div(
                [sidebar_item(item) for item in group["items"]],
                class_name="grid gap-1 mt-1 pl-2",
            ),
            None,
        ),
        class_name="mb-2",
    )


def sidebar() -> rx.Component:
    """The sidebar for the dashboard."""
    return rx.el.aside(
        rx.el.div(
            rx.el.a(
                rx.icon("leaf", class_name="h-8 w-8 text-emerald-500"), href="/"
            ),
            rx.cond(
                rx.cond(UIState.sidebar_collapsed, False, True),
                rx.el.span(
                    "AgriLedger",
                    class_name="text-xl font-bold text-stone-800 dark:text-stone-100",
                ),
                None,
            ),
            class_name="flex items-center gap-2 font-semibold p-4 border-b border-stone-200 dark:border-stone-700",
        ),
        # Main navigation — grouped accordion when expanded, icon rail when collapsed.
        rx.cond(
            UIState.sidebar_collapsed,
            rx.el.nav(
                [sidebar_icon_item(item) for item in ALL_NAV_ITEMS],
                class_name="grid items-start gap-2 p-4 text-sm font-medium overflow-y-auto",
            ),
            rx.el.nav(
                [sidebar_group(group) for group in NAV_GROUPS],
                class_name="grid items-start p-4 text-sm font-medium overflow-y-auto",
            ),
        ),
        rx.el.nav(
            rx.el.a(
                rx.icon("plus", class_name="h-5 w-5 flex-shrink-0"),
                rx.cond(
                    rx.cond(UIState.sidebar_collapsed, False, True),
                    rx.el.span(
                        I18nState.t["nav.add_transaction"],
                        class_name="truncate",
                    ),
                    None,
                ),
                href="/add-transaction",
                class_name="flex items-center gap-3 rounded-lg px-3 py-2 bg-emerald-500 text-white font-semibold hover:bg-emerald-600 transition-all shadow-sm active:scale-[0.98]",
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-5 w-5 flex-shrink-0"),
                rx.cond(
                    rx.cond(UIState.sidebar_collapsed, False, True),
                    rx.el.span(I18nState.t["nav.logout"], class_name="truncate"),
                    None,
                ),
                on_click=AuthState.logout,
                class_name="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-red-500 hover:bg-red-50 transition-all text-left dark:hover:bg-red-950/40 active:scale-[0.98]",
            ),
            class_name="mt-auto grid items-start p-4 text-sm font-medium gap-2",
        ),
        class_name=rx.cond(
            UIState.sidebar_collapsed,
            "hidden md:flex flex-col h-screen bg-cream-100 dark:bg-stone-950 border-r border-stone-200 dark:border-stone-800 transition-all w-20 overflow-y-auto",
            "hidden md:flex flex-col h-screen bg-cream-100 dark:bg-stone-950 border-r border-stone-200 dark:border-stone-800 transition-all w-64 overflow-y-auto",
        ),
    )


def mobile_nav_item(item: dict) -> rx.Component:
    """A nav link inside the mobile drawer (closes the drawer on click)."""
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5 flex-shrink-0"),
        rx.el.span(_nav_label(item), class_name="truncate"),
        href=item["href"],
        on_click=UIState.close_mobile_nav,
        class_name=rx.cond(
            _is_active(item["href"]),
            "flex items-center gap-3 rounded-lg px-3 py-3 min-h-[44px] text-emerald-600 bg-emerald-50 transition-all dark:bg-emerald-950 dark:text-emerald-400",
            "flex items-center gap-3 rounded-lg px-3 py-3 min-h-[44px] text-stone-600 hover:bg-stone-100 transition-all dark:text-stone-300 dark:hover:bg-stone-800",
        ),
    )


def mobile_nav_group(group: dict) -> rx.Component:
    """One section (header + items) inside the mobile drawer."""
    return rx.el.div(
        rx.el.div(
            rx.icon(group["icon"], class_name="h-4 w-4 text-stone-400"),
            rx.el.span(
                group["name"],
                class_name="text-[11px] font-bold uppercase tracking-wider text-stone-400",
            ),
            class_name="flex items-center gap-2 px-3 py-1.5",
        ),
        rx.el.div(
            [mobile_nav_item(item) for item in group["items"]],
            class_name="grid gap-1 pl-2",
        ),
        class_name="mb-3",
    )


def mobile_drawer() -> rx.Component:
    """Slide-in navigation drawer for phones (below the md breakpoint).

    Always rendered so the slide and fade transitions can animate in both
    directions; the panel is pushed off-screen and the backdrop is made
    non-interactive while closed.
    """
    return rx.el.div(
        rx.el.div(
            on_click=UIState.close_mobile_nav,
            class_name=rx.cond(
                UIState.mobile_nav_open,
                "fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden opacity-100 transition-opacity duration-300",
                "fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden opacity-0 pointer-events-none transition-opacity duration-300",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("leaf", class_name="h-8 w-8 text-emerald-500"),
                    href="/",
                    on_click=UIState.close_mobile_nav,
                ),
                rx.el.span(
                    "AgriLedger",
                    class_name="text-xl font-bold text-stone-800 dark:text-stone-100",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-5 w-5"),
                    on_click=UIState.close_mobile_nav,
                    class_name="ml-auto p-2 rounded-lg hover:bg-stone-100 transition-colors dark:hover:bg-stone-800",
                ),
                class_name="flex items-center gap-2 p-4 border-b border-stone-200 dark:border-stone-700",
            ),
            rx.el.nav(
                [mobile_nav_group(group) for group in NAV_GROUPS],
                class_name="p-4 text-sm font-medium overflow-y-auto",
            ),
            rx.el.div(
                rx.el.a(
                    rx.icon("plus", class_name="h-5 w-5 flex-shrink-0"),
                    rx.el.span("Add Transaction", class_name="truncate"),
                    href="/add-transaction",
                    on_click=UIState.close_mobile_nav,
                    class_name="flex items-center gap-3 rounded-lg px-3 py-2.5 bg-emerald-500 text-white font-semibold hover:bg-emerald-600 transition-all active:scale-[0.98]",
                ),
                install_app_button(),
                rx.el.button(
                    rx.icon("log-out", class_name="h-5 w-5 flex-shrink-0"),
                    rx.el.span(I18nState.t["nav.logout"], class_name="truncate"),
                    on_click=[UIState.close_mobile_nav, AuthState.logout],
                    class_name="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-red-500 hover:bg-red-50 transition-all text-left dark:hover:bg-red-950/40",
                ),
                class_name="mt-auto grid gap-2 p-4 border-t border-stone-200 dark:border-stone-700",
            ),
            class_name=rx.cond(
                UIState.mobile_nav_open,
                "fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col bg-cream-100 dark:bg-stone-950 shadow-2xl md:hidden transform translate-x-0 transition-transform duration-300 ease-in-out",
                "fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col bg-cream-100 dark:bg-stone-950 shadow-2xl md:hidden transform -translate-x-full transition-transform duration-300 ease-in-out",
            ),
        ),
    )


def mobile_bottom_item(item: dict) -> rx.Component:
    """One tab in the mobile bottom navigation bar."""
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5"),
        rx.el.span(_nav_label(item), class_name="text-[10px] font-medium"),
        href=item["href"],
        aria_label=item["name"],
        class_name=rx.cond(
            _is_active(item["href"]),
            "flex flex-1 flex-col items-center gap-0.5 py-2.5 min-h-[48px] text-emerald-600",
            "flex flex-1 flex-col items-center gap-0.5 py-2.5 min-h-[48px] text-stone-500 hover:text-stone-700 dark:text-stone-400 transition-colors dark:hover:text-stone-300",
        ),
    )


def mobile_bottom_nav() -> rx.Component:
    """Fixed bottom tab bar for phones (below the md breakpoint)."""
    return rx.el.nav(
        [mobile_bottom_item(item) for item in MOBILE_BOTTOM_ITEMS],
        rx.el.button(
            rx.icon("menu", class_name="h-5 w-5"),
            rx.el.span("More", class_name="text-[10px] font-medium"),
            on_click=UIState.toggle_mobile_nav,
            aria_label="Open full navigation menu",
            class_name="flex flex-1 flex-col items-center gap-0.5 py-2.5 min-h-[48px] text-stone-500 hover:text-stone-700 dark:text-stone-400 transition-colors dark:hover:text-stone-300",
        ),
        class_name="md:hidden fixed bottom-0 inset-x-0 z-30 flex items-stretch justify-around bg-white dark:bg-stone-900 border-t border-stone-200 dark:border-stone-700 pb-[env(safe-area-inset-bottom)]",
    )


def notifications_panel() -> rx.Component:
    """Dropdown panel listing recent notifications (anchored under the bell)."""
    return rx.cond(
        NotificationState.show_notifications,
        rx.el.div(
            # Invisible full-viewport backdrop: clicking anywhere outside the
            # panel closes it (critical on touch where re-tapping the bell is
            # awkward when the panel is nearly full-width on phones).
            rx.el.div(
                on_click=NotificationState.close_notifications,
                class_name="fixed inset-0 z-40",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h4(
                        "Notifications",
                        class_name="font-semibold text-stone-800 dark:text-stone-100",
                    ),
                    rx.cond(
                        NotificationState.unread_count > 0,
                        rx.el.span(
                            NotificationState.unread_count.to_string() + " new",
                            class_name="text-xs font-semibold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full dark:bg-emerald-950 dark:text-emerald-400",
                        ),
                        None,
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Mark all read",
                            on_click=NotificationState.mark_all_read,
                            class_name="text-xs text-emerald-600 hover:text-emerald-700 font-medium transition-colors px-2 py-1 min-h-[32px]",
                        ),
                        rx.el.button(
                            "Clear all",
                            on_click=NotificationState.clear_notifications,
                            class_name="text-xs text-stone-500 dark:text-stone-400 hover:text-stone-700 font-medium transition-colors px-2 py-1 min-h-[32px] dark:text-stone-400 dark:hover:text-stone-200",
                        ),
                        class_name="flex items-center gap-1",
                    ),
                    class_name="flex items-center justify-between gap-2 mb-3",
                ),
                rx.cond(
                    NotificationState.notifications.length() == 0,
                    rx.el.p(
                        "You're all caught up.",
                        class_name="text-sm text-stone-500 dark:text-stone-400 py-6 text-center dark:text-stone-400",
                    ),
                    rx.el.div(
                        rx.foreach(
                            NotificationState.notifications,
                            lambda n, i: rx.el.div(
                                rx.icon(
                                    rx.cond(
                                        n["type"] == "alert",
                                        "triangle-alert",
                                        rx.cond(
                                            n["type"] == "info",
                                            "info",
                                            "bell",
                                        ),
                                    ),
                                    class_name="h-4 w-4 text-emerald-600 flex-shrink-0 mt-0.5",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        n["title"],
                                        class_name="text-sm font-medium text-stone-800 dark:text-stone-100",
                                    ),
                                    rx.el.p(
                                        n["message"],
                                        class_name="text-xs text-stone-500 dark:text-stone-400",
                                    ),
                                    class_name="flex-1 min-w-0",
                                ),
                                rx.el.button(
                                    rx.icon("x", class_name="h-3.5 w-3.5"),
                                    on_click=lambda idx=i: NotificationState.dismiss_notification(
                                        idx
                                    ),
                                    class_name="p-1.5 rounded hover:bg-stone-100 text-stone-400 transition-colors dark:hover:bg-stone-700 min-w-[32px] min-h-[32px] flex items-center justify-center flex-shrink-0",
                                ),
                                class_name="flex items-start gap-2 p-2 rounded-lg hover:bg-stone-50 transition-colors dark:hover:bg-stone-800",
                            ),
                        ),
                        class_name="space-y-1 max-h-72 overflow-y-auto",
                    ),
                ),
                class_name="p-3",
            ),
            class_name="absolute right-0 top-full mt-2 w-[min(20rem,calc(100vw-1.5rem))] bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-700 rounded-xl shadow-xl z-50 al-modal-in",
        ),
        None,
    )


def theme_toggle_button() -> rx.Component:
    return rx.el.button(
        rx.icon(
            rx.cond(UIState.dark_mode, "sun", "moon"),
            class_name="h-5 w-5 text-stone-600 dark:text-stone-300",
        ),
        on_click=UIState.toggle_theme,
        aria_label="Toggle dark mode",
        class_name="p-2.5 rounded-full hover:bg-stone-200 transition-all active:scale-90 dark:hover:bg-stone-700 min-w-[40px] min-h-[40px] flex items-center justify-center",
    )


def language_switcher() -> rx.Component:
    """Compact language pill switcher (English / தமிழ் / हिन्दी)."""
    options = [("English", "EN"), ("Tamil", "தமிழ்"), ("Hindi", "हिं")]
    return rx.el.div(
        rx.foreach(
            options,
            lambda opt: rx.el.button(
                opt[1],
                on_click=lambda o=opt: I18nState.set_language(o[0]),
                class_name=rx.cond(
                    I18nState.language == opt[0],
                    "px-2.5 py-1.5 min-h-[32px] rounded-md text-xs font-semibold bg-emerald-500 text-white transition-all",
                    "px-2.5 py-1.5 min-h-[32px] rounded-md text-xs font-semibold text-stone-500 dark:text-stone-400 hover:bg-stone-100 transition-all dark:hover:bg-stone-700",
                ),
            ),
        ),
        class_name="flex items-center gap-1 bg-stone-100 dark:bg-stone-800 p-1 rounded-lg",
    )


def dashboard_header() -> rx.Component:
    """The header for the dashboard.

    Responsive strategy for small screens:
    - Language switcher hides below ``sm`` (full switcher lives in Settings).
    - Compact install button only shows when a prompt is available.
    - Farm name truncates with ``min-w-0`` so it never pushes controls off.
    """
    return rx.el.header(
        rx.el.div(
            # Mobile: hamburger opens the navigation drawer.
            rx.el.button(
                rx.icon("menu", class_name="h-5 w-5"),
                on_click=UIState.toggle_mobile_nav,
                aria_label="Open navigation menu",
                class_name="p-2.5 rounded-md hover:bg-stone-200 transition-colors md:hidden dark:hover:bg-stone-700 min-w-[40px] min-h-[40px] flex items-center justify-center",
            ),
            # Desktop: toggles the sidebar collapse state.
            rx.el.button(
                rx.icon("panel-left", class_name="h-5 w-5"),
                on_click=UIState.toggle_sidebar,
                aria_label="Toggle sidebar",
                class_name="p-2.5 rounded-md hover:bg-stone-200 transition-colors hidden md:flex dark:hover:bg-stone-700 min-w-[40px] min-h-[40px] items-center justify-center",
            ),
            rx.el.span(
                SettingsState.farm_name,
                class_name="font-semibold text-stone-800 dark:text-stone-100 truncate dark:text-stone-100 min-w-0",
            ),
            class_name="flex items-center gap-2 md:gap-4 min-w-0 flex-1",
        ),
        rx.el.div(
            # Language pills: hide on phones (Settings has the full switcher).
            rx.el.div(
                language_switcher(),
                class_name="hidden sm:flex",
            ),
            install_app_button(compact=True),
            theme_toggle_button(),
            # Notification bell + dropdown (unread badge when count > 0).
            rx.el.div(
                rx.el.button(
                    rx.icon("bell", class_name="h-5 w-5 text-stone-600 dark:text-stone-300"),
                    on_click=NotificationState.toggle_notifications,
                    aria_label="Open notifications",
                    class_name="relative p-2.5 rounded-full hover:bg-stone-200 transition-all active:scale-90 dark:hover:bg-stone-700 min-w-[40px] min-h-[40px] flex items-center justify-center",
                ),
                rx.cond(
                    NotificationState.unread_count > 0,
                    rx.el.span(
                        rx.cond(
                            NotificationState.unread_count > 9,
                            "9+",
                            NotificationState.unread_count.to_string(),
                        ),
                        class_name="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 flex items-center justify-center text-[10px] font-bold bg-red-500 text-white rounded-full al-pulse-once",
                    ),
                    None,
                ),
                notifications_panel(),
                class_name="relative",
            ),
            rx.el.a(
                rx.image(
                    src=f"https://api.dicebear.com/9.x/initials/svg?seed={AuthState.user_name}",
                    class_name="w-9 h-9 rounded-full border-2 border-emerald-500 transition-transform hover:scale-105",
                ),
                href="/settings",
                aria_label="Open settings",
                class_name="flex items-center justify-center min-w-[40px] min-h-[40px]",
            ),
            class_name="flex items-center gap-1.5 sm:gap-2 md:gap-3 flex-shrink-0",
        ),
        class_name="flex items-center justify-between h-16 px-3 md:px-6 border-b bg-white dark:bg-stone-900 dark:border-stone-700 gap-2",
    )


def dashboard_layout(content: rx.Component, page_title: str) -> rx.Component:
    """The layout for all dashboard pages."""
    return rx.el.div(
        sidebar(),
        rx.el.div(
            dashboard_header(),
            rx.el.main(
                rx.el.h1(
                    page_title,
                    class_name="text-2xl md:text-3xl font-bold text-stone-800 dark:text-stone-100 mb-4 md:mb-6 dark:text-stone-100 al-fade-up",
                ),
                content,
                class_name="flex-1 bg-stone-50 dark:bg-stone-950 relative px-4 pt-4 pb-24 md:px-6 md:pt-6 md:pb-6",
            ),
            class_name="flex flex-col flex-1",
        ),
        mobile_drawer(),
        mobile_bottom_nav(),
        quick_add_dialog(),
        on_mount=[
            UIState.close_mobile_nav,
            UIState.check_install_status,
            UIState.init_theme,
            NotificationState.load_notifications,
        ],
        class_name="flex min-h-screen w-full bg-cream-100 dark:bg-stone-950 font-['Lato']",
    )

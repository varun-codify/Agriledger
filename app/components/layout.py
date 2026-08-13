import reflex as rx

from app.components.common import install_app_button
from app.components.quick_add import quick_add_dialog
from app.states.auth_state import AuthState
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
                        class_name="text-xl font-bold text-stone-800 hidden sm:inline",
                    ),
                    class_name="flex items-center gap-2",
                ),
                href="/",
                aria_label="AgriLedger home page",
                class_name="focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded",
            ),
            # Desktop Navigation Links
            rx.el.div(
                rx.el.a(
                    "Features",
                    href="#features",
                    class_name="text-stone-600 hover:text-emerald-600 transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-2 py-1",
                    aria_label="View features",
                ),
                rx.el.a(
                    "About",
                    href="#about",
                    class_name="text-stone-600 hover:text-emerald-600 transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-2 py-1",
                    aria_label="Learn about us",
                ),
                rx.el.a(
                    "Pricing",
                    href="#pricing",
                    class_name="text-stone-600 hover:text-emerald-600 transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-2 py-1",
                    aria_label="View pricing plans",
                ),
                class_name="hidden md:flex items-center gap-8",
                role="navigation",
                aria_label="Primary navigation",
            ),
            # Auth Buttons
            rx.el.div(
                rx.el.a(
                    "Login",
                    href="/login",
                    class_name="text-stone-600 hover:text-emerald-600 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-2 py-1",
                    aria_label="Log in to your account",
                ),
                rx.el.a(
                    "Sign Up",
                    href="/register",
                    class_name="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-5 py-2.5 rounded-lg hover:from-emerald-600 hover:to-emerald-700 font-semibold transition-all shadow-sm hover:shadow-md focus:outline-none focus:ring-4 focus:ring-emerald-300",
                    aria_label="Create new account",
                    role="button",
                ),
                class_name="flex items-center gap-4",
                role="group",
                aria_label="Authentication options",
            ),
            class_name="max-w-7xl mx-auto flex items-center justify-between px-4 py-4",
            role="navigation",
            aria_label="Main navigation",
        ),
        class_name="bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-stone-200/50 shadow-sm",
        style={"scroll-behavior": "smooth"},
        role="banner",
    )


NAV_GROUPS = [
    {
        "name": "Farm",
        "icon": "tractor",
        "items": [
            {"name": "Dashboard", "icon": "layout-dashboard", "href": "/dashboard"},
            {"name": "Animals", "icon": "git-fork", "href": "/cattle"},
            {"name": "Breeding Cycles", "icon": "heart", "href": "/cattle/breeding"},
            {"name": "Crops", "icon": "sprout", "href": "/crops"},
        ],
    },
    {
        "name": "Dairy & Sales",
        "icon": "droplets",
        "items": [
            {"name": "Milk & Bills", "icon": "landmark", "href": "/milk"},
            {"name": "Transactions", "icon": "arrow-left-right", "href": "/transactions"},
        ],
    },
    {
        "name": "Intelligence",
        "icon": "brain-circuit",
        "items": [
            {"name": "Feed", "icon": "wheat", "href": "/feed"},
            {"name": "Insights & AI", "icon": "bot", "href": "/insights"},
        ],
    },
    {
        "name": "System",
        "icon": "cog",
        "items": [
            {"name": "Reports", "icon": "file-text", "href": "/reports"},
            {"name": "Settings", "icon": "settings", "href": "/settings"},
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
        rx.el.span(item["name"], class_name="truncate"),
        href=item["href"],
        class_name=rx.cond(
            _is_active(item["href"]),
            "flex items-center gap-3 rounded-lg px-3 py-2 text-emerald-600 bg-emerald-50 transition-all",
            "flex items-center gap-3 rounded-lg px-3 py-2 text-stone-600 hover:bg-stone-100 transition-all",
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
            "flex items-center justify-center rounded-lg p-2.5 text-emerald-600 bg-emerald-50 transition-all",
            "flex items-center justify-center rounded-lg p-2.5 text-stone-600 hover:bg-stone-100 transition-all",
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
                "h-4 w-4 ml-auto text-stone-400 transition-transform",
                "h-4 w-4 ml-auto text-stone-400 transition-transform -rotate-90",
            ),
        ),
        on_click=lambda: UIState.toggle_sidebar_group(group["name"]),
        class_name="flex w-full items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-stone-100 transition-colors",
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
                    "AgriLedger", class_name="text-xl font-bold text-stone-800"
                ),
                None,
            ),
            class_name="flex items-center gap-2 font-semibold p-4 border-b border-stone-200",
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
                    rx.el.span("Add Transaction", class_name="truncate"),
                    None,
                ),
                href="/add-transaction",
                class_name="flex items-center gap-3 rounded-lg px-3 py-2 bg-emerald-500 text-white font-semibold hover:bg-emerald-600 transition-all shadow-sm",
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-5 w-5 flex-shrink-0"),
                rx.cond(
                    rx.cond(UIState.sidebar_collapsed, False, True),
                    rx.el.span("Logout", class_name="truncate"),
                    None,
                ),
                on_click=AuthState.logout,
                class_name="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-red-500 hover:bg-red-50 transition-all text-left",
            ),
            class_name="mt-auto grid items-start p-4 text-sm font-medium gap-2",
        ),
        class_name=rx.cond(
            UIState.sidebar_collapsed,
            "hidden md:flex flex-col h-screen bg-cream-100 border-r border-stone-200 transition-all w-20 overflow-y-auto",
            "hidden md:flex flex-col h-screen bg-cream-100 border-r border-stone-200 transition-all w-64 overflow-y-auto",
        ),
    )


def mobile_nav_item(item: dict) -> rx.Component:
    """A nav link inside the mobile drawer (closes the drawer on click)."""
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5 flex-shrink-0"),
        rx.el.span(item["name"], class_name="truncate"),
        href=item["href"],
        on_click=UIState.close_mobile_nav,
        class_name=rx.cond(
            _is_active(item["href"]),
            "flex items-center gap-3 rounded-lg px-3 py-2.5 text-emerald-600 bg-emerald-50 transition-all",
            "flex items-center gap-3 rounded-lg px-3 py-2.5 text-stone-600 hover:bg-stone-100 transition-all",
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
                    "AgriLedger", class_name="text-xl font-bold text-stone-800"
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-5 w-5"),
                    on_click=UIState.close_mobile_nav,
                    class_name="ml-auto p-2 rounded-lg hover:bg-stone-100 transition-colors",
                ),
                class_name="flex items-center gap-2 p-4 border-b border-stone-200",
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
                    class_name="flex items-center gap-3 rounded-lg px-3 py-2.5 bg-emerald-500 text-white font-semibold hover:bg-emerald-600 transition-all",
                ),
                install_app_button(),
                rx.el.button(
                    rx.icon("log-out", class_name="h-5 w-5 flex-shrink-0"),
                    rx.el.span("Logout", class_name="truncate"),
                    on_click=[UIState.close_mobile_nav, AuthState.logout],
                    class_name="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-red-500 hover:bg-red-50 transition-all text-left",
                ),
                class_name="mt-auto grid gap-2 p-4 border-t border-stone-200",
            ),
            aria_hidden=rx.cond(UIState.mobile_nav_open, "false", "true"),
            class_name=rx.cond(
                UIState.mobile_nav_open,
                "fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col bg-cream-100 shadow-2xl md:hidden transform translate-x-0 transition-transform duration-300 ease-in-out",
                "fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col bg-cream-100 shadow-2xl md:hidden transform -translate-x-full transition-transform duration-300 ease-in-out",
            ),
        ),
    )


def mobile_bottom_item(item: dict) -> rx.Component:
    """One tab in the mobile bottom navigation bar."""
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5"),
        rx.el.span(item["name"], class_name="text-[10px] font-medium"),
        href=item["href"],
        aria_label=item["name"],
        class_name=rx.cond(
            _is_active(item["href"]),
            "flex flex-1 flex-col items-center gap-0.5 py-2 text-emerald-600",
            "flex flex-1 flex-col items-center gap-0.5 py-2 text-stone-500 hover:text-stone-700 transition-colors",
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
            class_name="flex flex-1 flex-col items-center gap-0.5 py-2 text-stone-500 hover:text-stone-700 transition-colors",
        ),
        class_name="md:hidden fixed bottom-0 inset-x-0 z-30 flex items-stretch justify-around bg-white border-t border-stone-200 pb-[env(safe-area-inset-bottom)]",
    )


def dashboard_header() -> rx.Component:
    """The header for the dashboard."""
    return rx.el.header(
        rx.el.div(
            # Mobile: hamburger opens the navigation drawer.
            rx.el.button(
                rx.icon("menu", class_name="h-5 w-5"),
                on_click=UIState.toggle_mobile_nav,
                aria_label="Open navigation menu",
                class_name="p-2 rounded-md hover:bg-stone-200 transition-colors md:hidden",
            ),
            # Desktop: toggles the sidebar collapse state.
            rx.el.button(
                rx.icon("panel-left", class_name="h-5 w-5"),
                on_click=UIState.toggle_sidebar,
                aria_label="Toggle sidebar",
                class_name="p-2 rounded-md hover:bg-stone-200 transition-colors hidden md:flex",
            ),
            rx.el.span(
                SettingsState.farm_name, class_name="font-semibold text-stone-800 truncate"
            ),
            class_name="flex items-center gap-4",
        ),
        rx.el.div(
            install_app_button(compact=True),
            rx.el.button(
                rx.icon("bell", class_name="h-5 w-5 text-stone-600"),
                class_name="p-2 rounded-full hover:bg-stone-200 transition-colors",
            ),
            rx.el.a(
                rx.image(
                    src=f"https://api.dicebear.com/9.x/initials/svg?seed={AuthState.current_user['name']}",
                    class_name="w-9 h-9 rounded-full border-2 border-emerald-500",
                ),
                href="/settings",
                aria_label="Open settings",
            ),
            class_name="flex items-center gap-4",
        ),
        class_name="flex items-center justify-between h-16 px-4 md:px-6 border-b bg-white",
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
                    class_name="text-2xl md:text-3xl font-bold text-stone-800 mb-4 md:mb-6",
                ),
                content,
                class_name="flex-1 bg-stone-50 relative px-4 pt-4 pb-24 md:px-6 md:pt-6 md:pb-6",
            ),
            class_name="flex flex-col flex-1",
        ),
        mobile_drawer(),
        mobile_bottom_nav(),
        quick_add_dialog(),
        on_mount=[UIState.close_mobile_nav, UIState.check_install_status],
        class_name="flex min-h-screen w-full bg-cream-100 font-['Lato']",
    )

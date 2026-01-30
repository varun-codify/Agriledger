import reflex as rx
from app.states.auth_state import AuthState
from app.states.ui_state import UIState


def landing_header() -> rx.Component:
    """The header for the landing page."""
    return rx.el.header(
        rx.el.nav(
            # Logo/Brand
            rx.el.a(
                rx.el.div(
                    rx.icon("leaf", class_name="h-7 w-7 text-emerald-500", aria_hidden="true"),
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


def sidebar_item(item: dict, index: int) -> rx.Component:
    """A single item in the sidebar."""
    return rx.el.a(
        rx.icon(item["icon"], class_name="h-5 w-5"),
        rx.cond(
            rx.cond(UIState.sidebar_collapsed, False, True),
            rx.el.span(item["name"], class_name="truncate"),
            None,
        ),
        href=item["href"],
        class_name=rx.cond(
            rx.State.router.page.path == item["href"].to_string(),
            "flex items-center gap-3 rounded-lg px-3 py-2 text-emerald-600 bg-emerald-50 transition-all",
            "flex items-center gap-3 rounded-lg px-3 py-2 text-stone-600 hover:bg-stone-100 transition-all",
        ),
    )


def sidebar() -> rx.Component:
    """The sidebar for the dashboard."""
    nav_items = [
        {"name": "Dashboard", "icon": "layout-dashboard", "href": "/dashboard"},
        {"name": "Analytics", "icon": "bar-chart-3", "href": "/analytics"},
        {"name": "Add Transaction", "icon": "plus-circle", "href": "/add-transaction"},
        {"name": "Animals", "icon": "git-fork", "href": "/cattle"},
        {"name": "Breeding Cycles", "icon": "heart", "href": "/cattle/breeding"},
        {"name": "Crops", "icon": "sprout", "href": "/crops"},
        {"name": "Farm Insights", "icon": "brain-circuit", "href": "/insights"},
        {"name": "Reports", "icon": "file-text", "href": "/reports"},
    ]
    return rx.el.aside(
        rx.el.div(
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
            rx.el.nav(
                rx.foreach(nav_items, sidebar_item),
                class_name="grid items-start p-4 text-sm font-medium gap-2",
            ),
        ),
        rx.el.nav(
            rx.el.a(
                rx.icon("settings", class_name="h-5 w-5"),
                rx.cond(
                    rx.cond(UIState.sidebar_collapsed, False, True),
                    rx.el.span("Settings", class_name="truncate"),
                    None,
                ),
                href="/settings",
                class_name="flex items-center gap-3 rounded-lg px-3 py-2 text-stone-600 hover:bg-stone-100 transition-all",
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-5 w-5"),
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
            "hidden md:flex flex-col h-screen bg-cream-100 border-r border-stone-200 transition-all w-20",
            "hidden md:flex flex-col h-screen bg-cream-100 border-r border-stone-200 transition-all w-64",
        ),
    )


def dashboard_header() -> rx.Component:
    """The header for the dashboard."""
    return rx.el.header(
        rx.el.div(
            rx.el.button(
                rx.icon("panel-left", class_name="h-5 w-5"),
                on_click=UIState.toggle_sidebar,
                class_name="p-2 rounded-md hover:bg-stone-200 transition-colors",
            ),
            rx.el.span("My Farm", class_name="font-semibold text-stone-800"),
            class_name="flex items-center gap-4",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("bell", class_name="h-5 w-5 text-stone-600"),
                class_name="p-2 rounded-full hover:bg-stone-200 transition-colors",
            ),
            rx.el.a(
                rx.image(
                    src=f"https://api.dicebear.com/9.x/initials/svg?seed={AuthState.current_user['name']}",
                    class_name="w-9 h-9 rounded-full border-2 border-emerald-500",
                ),
                href="/profile",
            ),
            class_name="flex items-center gap-4",
        ),
        class_name="flex items-center justify-between h-16 px-6 border-b bg-white",
    )


from app.components.quick_add import quick_add_dialog


def dashboard_layout(content: rx.Component, page_title: str) -> rx.Component:
    """The layout for all dashboard pages."""
    return rx.el.div(
        sidebar(),
        rx.el.div(
            dashboard_header(),
            rx.el.main(
                rx.el.h1(
                    page_title, class_name="text-3xl font-bold text-stone-800 mb-6"
                ),
                content,
                class_name="flex-1 p-6 bg-stone-50 relative",
            ),
            class_name="flex flex-col flex-1",
        ),
        quick_add_dialog(),
        class_name="flex min-h-screen w-full bg-cream-100 font-['Lato']",
    )
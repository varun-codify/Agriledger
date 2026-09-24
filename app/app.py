import json
from types import SimpleNamespace
from socketio import AsyncServer
import reflex as rx
from reflex.utils import format as reflex_format

# Must run before any component module that imports reflex_ag_grid:
# switches AG Grid to Community-only so no enterprise trial watermark renders.
from app.ag_grid_patch import (  # noqa: E402, F401
    _community_only_add_imports as _,
)

from app.api import app as api_app  # noqa: E402  # mounted via api_transformer

from app.components.common import segmented_control, spinner
from app.components.landing import landing_page
from app.components.layout import dashboard_layout, landing_header
from app.states.auth_state import AuthState
from app.states.ui_state import UIState

from app.components.dashboard import (
    breeding_alerts_card,
    coconut_sales_chart,
    expense_pie_chart,
    fat_percentage_trend_chart,
    milk_trend_line_chart,
    recent_transactions_list,
    reminders_card,
    snf_percentage_trend_chart,
    summary_card,
    weather_card,
)
from app.components.insights.ai_insights import health_score_card, insights_widget
from app.components.insights.insights_hub import insights_hub_page
from app.components.insights.milk_quality import quality_score_card, milk_quality_insights
from app.components.transactions.wizard import transaction_wizard
from app.components.cattle.cattle_list import cattle_management_page
from app.components.crops.crop_list import crop_management_page
from app.components.crops.disease_scanner import disease_scanner_page
from app.components.breeding.breeding_detail import breeding_detail_page
from app.components.breeding.breeding_list import breeding_list_page
from app.components.cattle.cattle_profile import cattle_profile_page
from app.components.crops.crop_profile import crop_profile_page
from app.components.reports.reports_page import reports_page
from app.components.settings.settings_page import settings_page
from app.components.transactions.transaction_table import transactions_page
from app.components.feed.feed_page import feed_page
from app.components.feed.feed_panels import feed_overview_cards
from app.components.milk.milk_page import milk_page
from app.states.ai_insights_state import AIInsightsState
from app.states.app_data_state import AppDataState
from app.states.breeding_state import BreedingState
from app.states.cattle_state import CattleState
from app.states.crop_state import CropState
from app.states.dashboard_state import DashboardState


def index() -> rx.Component:
    """The landing page."""
    return rx.el.div(
        landing_header(),
        landing_page(),
        class_name="bg-cream-100 font-['Lato']",
        style={"scroll-behavior": "smooth"},
    )


def login_page() -> rx.Component:
    """The login page."""
    email_error = AuthState.field_errors["email"]
    password_error = AuthState.field_errors["password"]
    return rx.el.div(
        rx.el.div(
            rx.el.a(
                rx.icon("leaf", class_name="h-8 w-8 text-emerald-500"),
                href="/",
                class_name="mb-8 block",
            ),
            rx.el.h2(
                "Welcome Back",
                class_name="text-3xl font-bold text-stone-800 dark:text-stone-100 al-fade-up",
            ),
            rx.el.p(
                "Log in to manage your farm.",
                class_name="text-stone-600 mt-2 dark:text-stone-400 al-fade-up",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.input(
                        placeholder="Email",
                        type="email",
                        name="email",
                        on_change=AuthState.clear_errors,
                        class_name=rx.cond(
                            email_error != "",
                            "w-full px-4 py-3 rounded-lg border-2 border-red-400 bg-red-50/50 text-stone-800 focus:ring-2 focus:ring-red-400 focus:border-transparent transition al-shake dark:bg-red-950/30 dark:text-stone-100",
                            "w-full px-4 py-3 rounded-lg border border-stone-300 bg-white text-stone-800 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100",
                        ),
                    ),
                    rx.cond(
                        email_error != "",
                        rx.el.p(
                            email_error,
                            class_name="text-red-500 text-sm mt-1 al-fade-up",
                        ),
                        None,
                    ),
                    rx.el.input(
                        placeholder="Password",
                        type="password",
                        name="password",
                        on_change=AuthState.clear_errors,
                        class_name=rx.cond(
                            password_error != "",
                            "w-full px-4 py-3 rounded-lg border-2 border-red-400 bg-red-50/50 text-stone-800 focus:ring-2 focus:ring-red-400 focus:border-transparent transition al-shake dark:bg-red-950/30 dark:text-stone-100",
                            "w-full px-4 py-3 rounded-lg border border-stone-300 bg-white text-stone-800 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100",
                        ),
                    ),
                    rx.cond(
                        password_error != "",
                        rx.el.p(
                            password_error,
                            class_name="text-red-500 text-sm mt-1 al-fade-up",
                        ),
                        None,
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.el.div(
                            rx.icon("flag_triangle_right", class_name="h-4 w-4 mr-2"),
                            AuthState.error_message,
                            class_name="text-red-500 text-sm flex items-center bg-red-50 p-2 rounded-md dark:bg-red-950/40",
                        ),
                        None,
                    ),
                    class_name="space-y-4 mt-8",
                ),
                rx.el.button(
                    rx.cond(
                        AuthState.is_loading,
                        spinner("h-5 w-5"),
                        rx.el.span("Log In"),
                    ),
                    type="submit",
                    disabled=AuthState.is_loading,
                    class_name="w-full bg-emerald-500 text-white mt-6 py-3 rounded-lg font-semibold hover:bg-emerald-600 transition shadow-sm active:scale-[0.98] disabled:opacity-60 flex items-center justify-center gap-2",
                ),
                on_submit=AuthState.login,
            ),
            rx.el.p(
                "Don't have an account? ",
                rx.el.a(
                    "Sign up",
                    href="/register",
                    class_name="font-semibold text-emerald-600 hover:text-emerald-700 transition-colors",
                ),
                class_name="mt-6 text-center text-stone-600 dark:text-stone-400",
            ),
            class_name="bg-white p-8 md:p-12 rounded-2xl shadow-lg w-full max-w-md al-modal-in dark:bg-stone-900 dark:border dark:border-stone-700",
        ),
        class_name="min-h-screen flex items-center justify-center bg-cream-100 font-['Lato'] p-4",
    )


def register_page() -> rx.Component:
    """The registration page."""
    def _input(placeholder: str, type_: str, name: str) -> rx.Component:
        err = AuthState.field_errors[name]
        base = "w-full px-4 py-3 rounded-lg focus:ring-2 transition dark:bg-stone-800 dark:text-stone-100 "
        ok = "border border-stone-300 bg-white text-stone-800 dark:bg-stone-800 dark:text-stone-100 focus:ring-emerald-500 focus:border-transparent dark:border-stone-600"
        bad = "border-2 border-red-400 bg-red-50/50 focus:ring-red-400 focus:border-transparent al-shake dark:bg-red-950/30"
        return rx.el.div(
            rx.el.input(
                placeholder=placeholder,
                type=type_,
                name=name,
                on_change=AuthState.clear_errors,
                class_name=rx.cond(err != "", base + bad, base + ok),
            ),
            rx.cond(
                err != "",
                rx.el.p(err, class_name="text-red-500 text-sm mt-1 al-fade-up"),
                None,
            ),
        )

    return rx.el.div(
        rx.el.div(
            rx.el.a(
                rx.icon("leaf", class_name="h-8 w-8 text-emerald-500"),
                href="/",
                class_name="mb-8 block",
            ),
            rx.el.h2(
                "Create Your Account",
                class_name="text-3xl font-bold text-stone-800 dark:text-stone-100 al-fade-up",
            ),
            rx.el.p(
                "Start managing your farm today.",
                class_name="text-stone-600 mt-2 dark:text-stone-400 al-fade-up",
            ),
            rx.el.form(
                rx.el.div(
                    _input("Full Name", "text", "name"),
                    _input("Email", "email", "email"),
                    _input("Password", "password", "password"),
                    _input("Confirm Password", "password", "confirm_password"),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.el.div(
                            rx.icon("flag_triangle_right", class_name="h-4 w-4 mr-2"),
                            AuthState.error_message,
                            class_name="text-red-500 text-sm flex items-center bg-red-50 p-2 rounded-md dark:bg-red-950/40",
                        ),
                        None,
                    ),
                    class_name="space-y-4 mt-8",
                ),
                rx.el.button(
                    rx.cond(
                        AuthState.is_loading,
                        spinner("h-5 w-5"),
                        rx.el.span("Create Account"),
                    ),
                    type="submit",
                    disabled=AuthState.is_loading,
                    class_name="w-full bg-emerald-500 text-white mt-6 py-3 rounded-lg font-semibold hover:bg-emerald-600 transition shadow-sm active:scale-[0.98] disabled:opacity-60 flex items-center justify-center gap-2",
                ),
                on_submit=AuthState.register,
            ),
            rx.el.p(
                "Already have an account? ",
                rx.el.a(
                    "Log in",
                    href="/login",
                    class_name="font-semibold text-emerald-600 hover:text-emerald-700 transition-colors",
                ),
                class_name="mt-6 text-center text-stone-600 dark:text-stone-400",
            ),
            class_name="bg-white p-8 md:p-12 rounded-2xl shadow-lg w-full max-w-md al-modal-in dark:bg-stone-900 dark:border dark:border-stone-700",
        ),
        class_name="min-h-screen flex items-center justify-center bg-cream-100 font-['Lato'] p-4",
    )


def _dashboard_skeleton() -> rx.Component:
    """Pulse skeleton shown while dashboard data is loading."""
    kpi = rx.el.div(
        rx.el.div(class_name="h-4 w-24 bg-stone-200 rounded animate-pulse dark:bg-stone-700"),
        rx.el.div(class_name="h-8 w-16 bg-stone-200 rounded mt-3 animate-pulse dark:bg-stone-700"),
        class_name="bg-white dark:bg-stone-900 p-5 rounded-2xl shadow-sm border border-stone-100 dark:border-stone-700",
    )
    chart = rx.el.div(
        rx.el.div(class_name="h-5 w-40 bg-stone-200 rounded animate-pulse dark:bg-stone-700"),
        rx.el.div(class_name="h-52 w-full bg-stone-100 rounded-xl mt-4 animate-pulse dark:bg-stone-800"),
        class_name="bg-white dark:bg-stone-900 p-5 rounded-2xl shadow-sm border border-stone-100 dark:border-stone-700",
    )
    return rx.el.div(
        rx.el.div(*([kpi] * 5), class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6"),
        rx.el.div(class_name="h-10 w-72 bg-stone-200 rounded-xl mt-6 animate-pulse dark:bg-stone-700"),
        rx.el.div(*([chart] * 2), class_name="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6"),
        class_name="al-fade-up",
    )


def _dashboard_kpis() -> rx.Component:
    """Top KPI strip — always visible across all dashboard tabs."""
    return rx.el.div(
        summary_card(
            {
                "title": "Total Lambs",
                "icon": "heart",
                "value": CattleState.total_lambs,
                "change": "",
                "change_type": "up",
            }
        ),
        summary_card(
            {
                "title": "Total Kids",
                "icon": "activity",
                "value": CattleState.total_kids,
                "change": "",
                "change_type": "up",
            }
        ),
        summary_card(
            {
                "title": "Coconuts Sold (Month)",
                "icon": "tree-palm",
                "value": DashboardState.total_coconuts_sold_month,
                "change": "",
                "change_type": "up",
            }
        ),
        summary_card(
            {
                "title": "Avg Fat % (Week)",
                "icon": "activity",
                "value": f"{DashboardState.avg_fat_percentage_week}%",
                "change": "",
                "change_type": "up",
            }
        ),
        summary_card(
            {
                "title": "Avg SNF % (Week)",
                "icon": "activity",
                "value": f"{DashboardState.avg_snf_percentage_week}%",
                "change": "",
                "change_type": "up",
            }
        ),
        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6",
    )


def _dashboard_tab_bar() -> rx.Component:
    """Segmented control that switches the dashboard body section."""
    return segmented_control(
        UIState.dashboard_tab,
        [
            ("overview", "Overview", "layout-dashboard"),
            ("analytics", "Analytics", "chart-column"),
            ("production", "Production", "wheat"),
        ],
        UIState.set_dashboard_tab,
        container_class="mb-6",
    )


def _dashboard_overview_tab() -> rx.Component:
    """Health, AI insights, weather, reminders, recent activity."""
    return rx.el.div(
        rx.el.div(
            health_score_card(),
            insights_widget(),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-6",
        ),
        rx.el.div(
            weather_card(),
            reminders_card(),
            class_name="mt-6 grid grid-cols-1 lg:grid-cols-6 gap-6",
        ),
        rx.el.div(
            recent_transactions_list(),
            breeding_alerts_card(),
            class_name="mt-6 grid grid-cols-1 lg:grid-cols-6 gap-6",
        ),
    )


def _dashboard_analytics_tab() -> rx.Component:
    """Financial + production charts."""
    return rx.el.div(
        rx.el.div(
            expense_pie_chart(),
            coconut_sales_chart(),
            class_name="grid grid-cols-1 lg:grid-cols-6 gap-6",
        ),
        rx.el.div(
            fat_percentage_trend_chart(),
            snf_percentage_trend_chart(),
            class_name="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6",
        ),
        rx.el.div(
            milk_trend_line_chart(),
            class_name="mt-6 grid grid-cols-1 lg:grid-cols-6 gap-6",
        ),
    )


def _dashboard_production_tab() -> rx.Component:
    """Milk quality + feed intelligence deep-dives."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Milk Quality",
                class_name="text-lg font-semibold text-stone-800 dark:text-stone-100",
            ),
            rx.el.a(
                "Open Milk & Society Bills →",
                href="/milk",
                class_name="text-sm font-semibold text-emerald-600 hover:text-emerald-700",
            ),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.div(
            quality_score_card(),
            milk_quality_insights(),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Feed Intelligence",
                    class_name="text-lg font-semibold text-stone-800 dark:text-stone-100",
                ),
                rx.el.a(
                    "Open Feed Module →",
                    href="/feed",
                    class_name="text-sm font-semibold text-emerald-600 hover:text-emerald-700",
                ),
                class_name="flex items-center justify-between mb-4 mt-8",
            ),
            feed_overview_cards(),
        ),
    )


def dashboard_page() -> rx.Component:
    """The main dashboard page (KPI strip + tabbed body)."""
    return dashboard_layout(
        rx.cond(
            AppDataState.is_loading,
            _dashboard_skeleton(),
            rx.el.div(
                _dashboard_kpis(),
                rx.el.div(class_name="h-6"),
                _dashboard_tab_bar(),
                rx.cond(
                    UIState.dashboard_tab == "overview",
                    _dashboard_overview_tab(),
                    rx.cond(
                        UIState.dashboard_tab == "analytics",
                        _dashboard_analytics_tab(),
                        _dashboard_production_tab(),
                    ),
                ),
            ),
        ),
        page_title="Dashboard Overview",
    )


def add_transaction_page():
    return dashboard_layout(transaction_wizard(), "Add New Transaction")


def cattle_page():
    return dashboard_layout(cattle_management_page(), "Animal Management")


def crops_page():
    return dashboard_layout(crop_management_page(), "Crop Management")


def breeding_page_route():
    return dashboard_layout(breeding_list_page(), "Breeding Cycles")


def breeding_detail_page_route():
    return dashboard_layout(breeding_detail_page(), "Breeding Cycle Details")


custom_sio = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    cors_credentials=True,
    max_http_buffer_size=100 * 1024 * 1024,  # 100 MB max buffer size
    ping_interval=25,
    ping_timeout=120,
    json=SimpleNamespace(
        dumps=staticmethod(reflex_format.json_dumps),
        loads=staticmethod(json.loads),
    ),
    transports=["websocket", "polling"],
)


app = rx.App(
    sio=custom_sio,
    # Mount the FastAPI REST API inside the Reflex server: one process/port
    # serves UI, websockets, and API, and GZip compresses everything.
    api_transformer=api_app,
    stylesheets=["/style.css"],
    theme=rx.theme(
        appearance="light",
        props={"Button": {"radius": "medium"}, "TextField": {"radius": "medium"}},
    ),
    head_components=[
        # Restores saved theme + ResizeObserver guard (never force-locks light).
        rx.el.script(src="/ag_patch.js"),
        # Landing scroll-reveal (no-ops on pages without .reveal-on-scroll).
        rx.el.script(src="/reveal.js"),
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
            rel="stylesheet",
        ),
        # ── PWA / mobile-app metadata ──────────────────────────────────
        # ``viewport-fit=cover`` enables safe-area insets on notched phones;
        # placed after Reflex's default viewport tag so it takes precedence.
        rx.el.meta(
            name="viewport",
            content="width=device-width, initial-scale=1, viewport-fit=cover",
        ),
        rx.el.meta(name="theme-color", content="#10b981"),
        rx.el.link(rel="manifest", href="/manifest.json"),
        rx.el.link(rel="icon", type="image/png", href="/icon-192.png"),
        rx.el.link(rel="apple-touch-icon", href="/apple-touch-icon-180.png"),
        rx.el.meta(name="apple-mobile-web-app-capable", content="yes"),
        rx.el.meta(name="apple-mobile-web-app-status-bar-style", content="default"),
        rx.script(
            "if ('serviceWorker' in navigator) {"
            " window.addEventListener('load', function() {"
            " navigator.serviceWorker.register('/sw.js').catch(function() {});"
            " });"
            "}"
        ),
        # If the window crosses into desktop (>= md), the mobile drawer is
        # hidden by CSS — make sure any scroll lock it applied is released.
        rx.script(
            "window.matchMedia('(min-width: 768px)').addEventListener("
            " 'change', function(e) {"
            "  if (e.matches) { document.body.style.overflow = ''; }"
            " });"
        ),
        # Capture the browser's install prompt so we can show it on demand
        # (suppressing the automatic mini-infobar) from an in-app button.
        rx.script(
            "window.addEventListener('beforeinstallprompt', function(e) {"
            " e.preventDefault();"
            " window.__agriledgerDeferredPrompt = e;"
            "});"
            "window.addEventListener('appinstalled', function() {"
            " window.__agriledgerDeferredPrompt = null;"
            "});"
        ),
    ],
)

app.add_page(index, route="/")
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(
    dashboard_page,
    route="/dashboard",
    on_load=[
        AuthState.require_login,
        AppDataState.load_dashboard_data,
        UIState.set_dashboard_tab("overview"),
    ],
)
app.add_page(
    add_transaction_page, route="/add-transaction", on_load=AuthState.require_login
)
app.add_page(
    cattle_page,
    route="/cattle",
    on_load=[AuthState.require_login, AppDataState.load_page_data],
)
app.add_page(
    breeding_page_route,
    route="/cattle/breeding",
    on_load=[AuthState.require_login, AppDataState.load_page_data],
)
app.add_page(
    breeding_detail_page_route,
    route="/cattle/breeding/[id]",
    on_load=[
        AuthState.require_login,
        AppDataState.load_page_data,
        BreedingState.load_breeding_detail,
    ],
)
app.add_page(
    cattle_profile_page,
    route="/cattle/[id]",
    on_load=[
        AuthState.require_login,
        AppDataState.load_page_data,
        CattleState.load_cattle_profile,
    ],
)
app.add_page(
    disease_scanner_page,
    route="/disease-scanner",
    on_load=[AuthState.require_login, AppDataState.load_page_data],
)
app.add_page(
    disease_scanner_page,
    route="/crops/disease-scanner",
    on_load=[AuthState.require_login, AppDataState.load_page_data],
)
app.add_page(
    crops_page,
    route="/crops",
    on_load=[AuthState.require_login, AppDataState.load_page_data],
)
app.add_page(
    crop_profile_page,
    route="/crops/[id]",
    on_load=[
        AuthState.require_login,
        AppDataState.load_page_data,
        CropState.load_crop_profile,
    ],
)
app.add_page(
    feed_page,
    route="/feed",
    on_load=[AuthState.require_login, AppDataState.load_page_data],
)
app.add_page(
    insights_hub_page,
    route="/insights",
    on_load=[
        AuthState.require_login,
        AppDataState.load_insights_data,
        AIInsightsState.refresh_insights,
    ],
)
app.add_page(
    milk_page,
    route="/milk",
    on_load=[AuthState.require_login, AppDataState.load_page_data],
)
app.add_page(
    reports_page,
    route="/reports",
    on_load=[AuthState.require_login, AppDataState.load_reports_data],
)
app.add_page(
    settings_page,
    route="/settings",
    on_load=[AuthState.require_login, AppDataState.load_settings_data],
)
app.add_page(
    transactions_page,
    route="/transactions",
    on_load=[AuthState.require_login, AppDataState.load_page_data],
)

# Routes that were consolidated into other pages still work for old links —
# they simply forward the user to the new home of that content.
_REDIRECT_ROUTES = {
    "/analytics": "/dashboard",
    "/transactions-table": "/transactions",
    "/cattle-table": "/cattle",
    "/breeding-table": "/cattle/breeding",
    "/feed/analytics": "/feed",
    "/ai-assistant": "/insights",
}


def _make_redirect_page(old_route: str, target: str):
    def redirect_page() -> rx.Component:
        return rx.fragment()

    redirect_page.__name__ = f"redirect_{old_route.strip('/').replace('/', '_') or 'root'}"
    app.add_page(
        redirect_page,
        route=old_route,
        on_load=[AuthState.require_login, rx.redirect(target)],
    )


for _old, _target in _REDIRECT_ROUTES.items():
    _make_redirect_page(_old, _target)

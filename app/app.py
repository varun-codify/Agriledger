import reflex as rx
from app.states.auth_state import AuthState
from app.components.layout import landing_header, dashboard_layout
from app.components.landing import landing_page


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
    return rx.el.div(
        rx.el.div(
            rx.el.a(
                rx.icon("leaf", class_name="h-8 w-8 text-emerald-500"),
                href="/",
                class_name="mb-8",
            ),
            rx.el.h2("Welcome Back", class_name="text-3xl font-bold text-stone-800"),
            rx.el.p("Log in to manage your farm.", class_name="text-stone-600 mt-2"),
            rx.el.form(
                rx.el.div(
                    rx.el.input(
                        placeholder="Email",
                        type="email",
                        name="email",
                        class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition",
                    ),
                    rx.el.input(
                        placeholder="Password",
                        type="password",
                        name="password",
                        class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition",
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.el.div(
                            rx.icon("flag_triangle_right", class_name="h-4 w-4 mr-2"),
                            AuthState.error_message,
                            class_name="text-red-500 text-sm flex items-center bg-red-50 p-2 rounded-md",
                        ),
                        None,
                    ),
                    class_name="space-y-4 mt-8",
                ),
                rx.el.button(
                    "Log In",
                    type="submit",
                    class_name="w-full bg-emerald-500 text-white mt-6 py-3 rounded-lg font-semibold hover:bg-emerald-600 transition shadow-sm",
                ),
                on_submit=AuthState.login,
                reset_on_submit=True,
            ),
            rx.el.p(
                "Don't have an account? ",
                rx.el.a(
                    "Sign up",
                    href="/register",
                    class_name="font-semibold text-emerald-600",
                ),
                class_name="mt-6 text-center text-stone-600",
            ),
            class_name="bg-white p-8 md:p-12 rounded-2xl shadow-lg w-full max-w-md",
        ),
        class_name="min-h-screen flex items-center justify-center bg-cream-100 font-['Lato'] p-4",
    )


def register_page() -> rx.Component:
    """The registration page."""
    return rx.el.div(
        rx.el.div(
            rx.el.a(
                rx.icon("leaf", class_name="h-8 w-8 text-emerald-500"),
                href="/",
                class_name="mb-8",
            ),
            rx.el.h2(
                "Create Your Account", class_name="text-3xl font-bold text-stone-800"
            ),
            rx.el.p(
                "Start managing your farm today.", class_name="text-stone-600 mt-2"
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.input(
                        placeholder="Full Name",
                        name="name",
                        class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 transition",
                    ),
                    rx.el.input(
                        placeholder="Email",
                        type="email",
                        name="email",
                        class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 transition",
                    ),
                    rx.el.input(
                        placeholder="Password",
                        type="password",
                        name="password",
                        class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 transition",
                    ),
                    rx.el.input(
                        placeholder="Confirm Password",
                        type="password",
                        name="confirm_password",
                        class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 transition",
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.el.div(
                            rx.icon("flag_triangle_right", class_name="h-4 w-4 mr-2"),
                            AuthState.error_message,
                            class_name="text-red-500 text-sm flex items-center bg-red-50 p-2 rounded-md",
                        ),
                        None,
                    ),
                    class_name="space-y-4 mt-8",
                ),
                rx.el.button(
                    "Create Account",
                    type="submit",
                    class_name="w-full bg-emerald-500 text-white mt-6 py-3 rounded-lg font-semibold hover:bg-emerald-600 transition shadow-sm",
                ),
                on_submit=AuthState.register,
                reset_on_submit=True,
            ),
            rx.el.p(
                "Already have an account? ",
                rx.el.a(
                    "Log in", href="/login", class_name="font-semibold text-emerald-600"
                ),
                class_name="mt-6 text-center text-stone-600",
            ),
            class_name="bg-white p-8 md:p-12 rounded-2xl shadow-lg w-full max-w-md",
        ),
        class_name="min-h-screen flex items-center justify-center bg-cream-100 font-['Lato'] p-4",
    )


from app.components.dashboard import (
    summary_card,
    expense_pie_chart,
    profit_loss_bar_chart,
    milk_trend_line_chart,
    weather_card,
    reminders_card,
    recent_transactions_list,
    breeding_alerts_card,
    coconut_sales_chart,
    fat_percentage_trend_chart,
    snf_percentage_trend_chart,
    project_download_button,
)
from app.states.dashboard_state import DashboardState
from app.states.cattle_state import CattleState
from app.components.insights.ai_insights import health_score_card, insights_widget


def dashboard_page() -> rx.Component:
    """The main dashboard page."""
    return dashboard_layout(
        rx.el.div(
            rx.el.div(
                summary_card(
                    {
                        "title": "Total Lambs",
                        "icon": "sheep",
                        "value": CattleState.total_lambs,
                        "change": "",
                        "change_type": "up",
                    }
                ),
                summary_card(
                    {
                        "title": "Total Kids",
                        "icon": "goat",
                        "value": CattleState.total_kids,
                        "change": "",
                        "change_type": "up",
                    }
                ),
                summary_card(
                    {
                        "title": "Coconuts Sold (Month)",
                        "icon": "palm-tree",
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
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6",
            ),
            rx.el.div(
                health_score_card(),
                insights_widget(),
                class_name="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6",
            ),
            rx.el.div(
                expense_pie_chart(),
                breeding_alerts_card(),
                coconut_sales_chart(),
                class_name="mt-6 grid grid-cols-1 lg:grid-cols-6 gap-6",
            ),
            rx.el.div(
                fat_percentage_trend_chart(),
                snf_percentage_trend_chart(),
                class_name="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6",
            ),
            rx.el.div(
                milk_trend_line_chart(),
                recent_transactions_list(),
                class_name="mt-6 grid grid-cols-1 lg:grid-cols-6 gap-6",
            ),
            rx.el.div(
                weather_card(),
                reminders_card(),
                class_name="mt-6 grid grid-cols-1 lg:grid-cols-6 gap-6",
            ),
            project_download_button(),
        ),
        page_title="Dashboard Overview",
    )


def analytics_page():
    return dashboard_layout(
        rx.el.div(
            profit_loss_bar_chart(), milk_trend_line_chart(), class_name="space-y-6"
        ),
        page_title="Analytics Overview",
    )


from app.components.transactions.wizard import transaction_wizard


def add_transaction_page():
    return dashboard_layout(transaction_wizard(), "Add New Transaction")


from app.components.cattle.cattle_list import cattle_management_page, add_cattle_dialog


def cattle_page():
    return dashboard_layout(cattle_management_page(), "Animal Management")


from app.components.crops.crop_list import crop_management_page


def crops_page():
    return dashboard_layout(crop_management_page(), "Crop Management")


from app.components.cattle.cattle_profile import cattle_profile_page
from app.components.crops.crop_profile import crop_profile_page
from app.components.crops.farm_insights import farm_insights_page
from app.states.crop_state import CropState
from app.components.breeding.breeding_list import breeding_list_page
from app.components.breeding.breeding_detail import breeding_detail_page
from app.states.breeding_state import BreedingState
from app.components.reports.reports_page import reports_page
from app.components.settings.settings_page import settings_page


def farm_insights_page_route():
    return dashboard_layout(farm_insights_page(), "Farm Insights & Weather")


def breeding_page_route():
    return dashboard_layout(breeding_list_page(), "Breeding Cycles")


def breeding_detail_page_route():
    return dashboard_layout(breeding_detail_page(), "Breeding Cycle Details")


app = rx.App(
    theme=rx.theme(
        appearance="light",
        props={"Button": {"radius": "medium"}, "TextField": {"radius": "medium"}},
    ),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
from app.states.transaction_state import TransactionState
from app.states.crop_state import CropState
from app.states.breeding_state import BreedingState
from app.states.cattle_state import CattleState
from app.states.download_state import DownloadState

app.add_page(index, route="/")
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(
    dashboard_page,
    route="/dashboard",
    on_load=[
        AuthState.require_login,
        CattleState.fetch_cattle_list,
        TransactionState.fetch_transactions,
        CropState.fetch_crops_list,
        BreedingState.fetch_breeding_cycles,
    ],
)
app.add_page(analytics_page, route="/analytics", on_load=AuthState.require_login)
app.add_page(
    add_transaction_page, route="/add-transaction", on_load=AuthState.require_login
)
app.add_page(
    cattle_page,
    route="/cattle",
    on_load=[AuthState.require_login, CattleState.fetch_cattle_list],
)
app.add_page(
    breeding_page_route,
    route="/cattle/breeding",
    on_load=[
        AuthState.require_login,
        BreedingState.fetch_breeding_cycles,
        CattleState.fetch_cattle_list,
    ],
)
app.add_page(
    breeding_detail_page_route,
    route="/cattle/breeding/[id]",
    on_load=[
        AuthState.require_login,
        BreedingState.fetch_breeding_cycles,
        BreedingState.load_breeding_detail,
    ],
)
app.add_page(
    cattle_profile_page,
    route="/cattle/[id]",
    on_load=[
        AuthState.require_login,
        CattleState.fetch_cattle_list,
        CattleState.load_cattle_profile,
    ],
)
app.add_page(
    crops_page,
    route="/crops",
    on_load=[AuthState.require_login, CropState.fetch_crops_list],
)
app.add_page(
    crop_profile_page,
    route="/crops/[id]",
    on_load=[
        AuthState.require_login,
        CropState.fetch_crops_list,
        CropState.load_crop_profile,
    ],
)
app.add_page(
    farm_insights_page_route, route="/insights", on_load=AuthState.require_login
)
app.add_page(reports_page, route="/reports", on_load=AuthState.require_login)
app.add_page(settings_page, route="/settings", on_load=AuthState.require_login)
import reflex as rx

from app.states.breeding_state import BreedingState
from app.states.dashboard_state import DashboardState
from app.states.transaction_state import TransactionState


def summary_card(metric: rx.Var[dict]) -> rx.Component:
    """A reusable card for displaying a summary metric."""
    return rx.el.div(
        rx.el.div(
            rx.el.p(metric["title"], class_name="text-sm font-medium text-stone-500"),
            rx.icon(metric["icon"], class_name="h-6 w-6 text-stone-400"),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.el.h3(metric["value"], class_name="text-2xl font-bold text-stone-800"),
            rx.el.div(
                rx.icon(
                    rx.cond(
                        metric["change_type"] == "up",
                        "arrow-up-circle",
                        "arrow-down-circle",
                    ),
                    class_name=rx.cond(
                        metric["change_type"] == "up",
                        "h-4 w-4 text-emerald-500",
                        "h-4 w-4 text-red-500",
                    ),
                ),
                rx.el.span(metric["change"], class_name="text-xs text-stone-500"),
                class_name="flex items-center gap-1",
            ),
            class_name="flex items-end justify-between mt-2",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def breeding_alerts_card() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Breeding Alerts", class_name="text-lg font-semibold text-stone-800 mb-4"
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("clipboard-check", class_name="h-5 w-5 text-yellow-600"),
                rx.el.div(
                    rx.el.p(
                        f"{BreedingState.pregnancy_checks_due.length()} Checks Due",
                        class_name="font-medium text-stone-700",
                    ),
                    rx.el.p(
                        "Confirm pregnancy for due animals.",
                        class_name="text-xs text-stone-500",
                    ),
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.div(
                rx.icon("siren", class_name="h-5 w-5 text-red-600"),
                rx.el.div(
                    rx.el.p(
                        f"{BreedingState.calvings_due_soon.length()} Calvings Expected",
                        class_name="font-medium text-stone-700",
                    ),
                    rx.el.p(
                        "Animals expecting to give birth soon.",
                        class_name="text-xs text-stone-500",
                    ),
                ),
                class_name="flex items-center gap-3",
            ),
            class_name="space-y-4",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-1 lg:col-span-2",
    )


def fat_percentage_trend_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Milk Fat % Trend (30 Days)",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(cursor={"fill": "rgba(231, 229, 228, 0.4)"}),
            rx.recharts.x_axis(data_key="day", class_name="text-xs"),
            rx.recharts.y_axis(
                domain=["dataMin - 0.5", "dataMax + 0.5"], class_name="text-xs"
            ),
            rx.recharts.line(
                data_key="fat_percentage",
                stroke="#8884d8",
                stroke_width=2,
                type_="monotone",
            ),
            data=DashboardState.milk_fat_trend_data,
            height=250,
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def snf_percentage_trend_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Milk SNF % Trend (30 Days)",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(cursor={"fill": "rgba(231, 229, 228, 0.4)"}),
            rx.recharts.x_axis(data_key="day", class_name="text-xs"),
            rx.recharts.y_axis(
                domain=["dataMin - 0.5", "dataMax + 0.5"], class_name="text-xs"
            ),
            rx.recharts.line(
                data_key="snf_percentage",
                stroke="#82ca9d",
                stroke_width=2,
                type_="monotone",
            ),
            data=DashboardState.milk_snf_trend_data,
            height=250,
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def coconut_sales_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Coconut Sales (Last 6 Months)",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(cursor={"fill": "rgba(231, 229, 228, 0.4)"}),
            rx.recharts.x_axis(data_key="month", class_name="text-xs"),
            rx.recharts.y_axis(
                y_axis_id="left",
                orientation="left",
                stroke="#8884d8",
                class_name="text-xs",
            ),
            rx.recharts.y_axis(
                y_axis_id="right",
                orientation="right",
                stroke="#82ca9d",
                class_name="text-xs",
            ),
            rx.recharts.bar(
                data_key="volume", fill="#8884d8", radius=[4, 4, 0, 0], y_axis_id="left"
            ),
            rx.recharts.bar(
                data_key="revenue",
                fill="#82ca9d",
                radius=[4, 4, 0, 0],
                y_axis_id="right",
            ),
            data=DashboardState.coconut_sales_data,
            height=300,
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-1 lg:col-span-4",
    )


def expense_pie_chart() -> rx.Component:
    """A pie chart showing expense distribution."""
    return rx.el.div(
        rx.el.h3(
            "Expense Breakdown", class_name="text-lg font-semibold text-stone-800"
        ),
        rx.el.div(
            rx.recharts.pie_chart(
                rx.recharts.graphing_tooltip(cursor=False),
                rx.recharts.pie(
                    rx.foreach(
                        DashboardState.expense_data,
                        lambda item, index: rx.recharts.cell(fill=item["fill"]),
                    ),
                    data=DashboardState.expense_data,
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    inner_radius=60,
                    outer_radius=80,
                    padding_angle=5,
                    stroke="#ffffff",
                    stroke_width=2,
                    on_mouse_enter=DashboardState.on_pie_mouse_enter,
                    on_mouse_leave=DashboardState.on_pie_mouse_leave,
                ),
                width=300,
                height=250,
            ),
            rx.el.div(
                rx.cond(
                    DashboardState.active_pie_slice_name != "",
                    rx.el.div(
                        rx.el.p(
                            DashboardState.active_pie_slice_value,
                            class_name="text-2xl font-bold text-stone-800",
                        ),
                        rx.el.p(
                            DashboardState.active_pie_slice_name,
                            class_name="text-sm text-stone-500",
                        ),
                        class_name="text-center transition-opacity",
                    ),
                    rx.el.div(
                        rx.el.p("Total", class_name="text-sm text-stone-500"),
                        rx.el.p(
                            "₹" + DashboardState.total_expenses.to_string(),
                            class_name="text-2xl font-bold text-stone-800",
                        ),
                        class_name="text-center transition-opacity",
                    ),
                ),
                class_name="absolute inset-0 flex items-center justify-center",
            ),
            class_name="relative",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-1 lg:col-span-2",
    )


def milk_trend_line_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Milk Production Trend",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(
                vertical=False, stroke_dasharray="3 3", class_name="stroke-stone-200"
            ),
            rx.recharts.graphing_tooltip(cursor={"fill": "rgba(231, 229, 228, 0.4)"}),
            rx.recharts.x_axis(
                data_key="day",
                tick_line=False,
                axis_line=False,
                class_name="text-xs text-stone-500",
            ),
            rx.recharts.y_axis(
                tick_line=False, axis_line=False, class_name="text-xs text-stone-500"
            ),
            rx.recharts.line(
                data_key="liters",
                stroke="#3b82f6",
                stroke_width=2,
                dot=False,
                type_="monotone",
            ),
            data=DashboardState.milk_production_data,
            height=300,
            class_name="w-full",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-1 lg:col-span-3",
    )


def weather_card() -> rx.Component:
    """A card displaying weather highlights."""
    return rx.el.div(
        rx.el.div(
            rx.el.p("Weather Today", class_name="text-sm font-medium text-stone-500"),
            rx.icon(
                DashboardState.weather_highlight["icon"],
                class_name="h-6 w-6 text-yellow-500",
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.el.p(
                DashboardState.weather_highlight["temp"],
                class_name="text-2xl font-bold text-stone-800",
            ),
            rx.el.p(
                DashboardState.weather_highlight["condition"],
                class_name="text-sm text-stone-600",
            ),
            class_name="mt-2",
        ),
        rx.el.p(
            DashboardState.weather_highlight["tip"],
            class_name="text-xs text-stone-500 mt-4",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-1 lg:col-span-2",
    )


def reminders_card() -> rx.Component:
    """A card displaying upcoming reminders."""
    return rx.el.div(
        rx.el.h3("Reminders", class_name="text-lg font-semibold text-stone-800 mb-4"),
        rx.el.div(
            rx.foreach(
                DashboardState.reminders,
                lambda reminder: rx.el.div(
                    rx.icon(reminder["icon"], class_name="h-5 w-5 text-emerald-600"),
                    rx.el.div(
                        rx.el.p(
                            reminder["task"],
                            class_name="text-sm font-medium text-stone-700",
                        ),
                        rx.el.p(reminder["due"], class_name="text-xs text-stone-500"),
                    ),
                    class_name="flex items-center gap-3",
                ),
            ),
            class_name="space-y-4",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-1 lg:col-span-2",
    )


def recent_transactions_list() -> rx.Component:
    """A list of recent transactions for the dashboard."""
    return rx.el.div(
        rx.el.h3(
            "Recent Transactions",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.el.div(
            rx.cond(
                TransactionState.transactions.length() == 0,
                rx.el.div(
                    rx.icon(
                        "receipt-text", class_name="h-10 w-10 text-stone-300 mx-auto"
                    ),
                    rx.el.p(
                        "No transactions yet.",
                        class_name="text-center text-stone-500 mt-2 text-sm",
                    ),
                    class_name="py-10",
                ),
                rx.foreach(
                    TransactionState.recent_transactions,
                    lambda tx: rx.el.div(
                        rx.el.div(
                            rx.icon(
                                tx["category"]["icon"],
                                class_name="h-6 w-6 p-1 rounded-md bg-stone-100 text-stone-600",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    tx["category"]["name"],
                                    class_name="font-medium text-stone-800 text-sm",
                                ),
                                rx.el.p(
                                    tx["date"], class_name="text-xs text-stone-500"
                                ),
                            ),
                            class_name="flex items-center gap-3",
                        ),
                        rx.el.p(
                            rx.cond(tx["type"] == "income", "+", "-")
                            + "₹"
                            + tx["amount"].to_string(),
                            class_name=rx.cond(
                                tx["type"] == "income",
                                "text-emerald-500 font-semibold text-sm",
                                "text-red-500 font-semibold text-sm",
                            ),
                        ),
                        class_name="flex items-center justify-between p-2 rounded-lg hover:bg-stone-50",
                    ),
                ),
            ),
            class_name="space-y-2 mt-2",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-1 lg:col-span-3",
    )




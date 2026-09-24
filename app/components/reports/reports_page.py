"""Reports & Export page with PDF and Excel generation.

Provides comprehensive farm reports with financial summaries,
animal profitability, and exportable formats.
"""

import reflex as rx

from app.components.common import BTN_PRIMARY, spinner
from app.states.reports_state import ReportsState


def date_range_selector() -> rx.Component:
    """Date range selection buttons."""
    ranges = ["Last 30 Days", "Last Month", "This Year"]
    return rx.el.div(
        rx.el.h3(
            "Date Range",
            class_name="text-lg font-semibold text-stone-800 mb-3 dark:text-stone-100",
        ),
        rx.el.div(
            rx.foreach(
                ranges,
                lambda r: rx.el.button(
                    r,
                    on_click=lambda: ReportsState.set_date_range(r),
                    class_name=rx.cond(
                        ReportsState.date_range == r,
                        "px-4 py-2.5 min-h-[40px] rounded-lg bg-emerald-500 text-white font-semibold text-sm transition-all active:scale-[0.98]",
                        "px-4 py-2.5 min-h-[40px] rounded-lg bg-white text-stone-600 font-semibold text-sm border border-stone-200 hover:bg-stone-50 transition-all active:scale-[0.98] dark:bg-stone-800 dark:text-stone-300 dark:border-stone-700 dark:hover:bg-stone-700",
                    ),
                ),
            ),
            class_name="flex gap-2 flex-wrap",
        ),
    )


def summary_metric_card(
    icon: str, label: str, value: rx.Var, color_class: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-6 w-6 {color_class}"),
            class_name="p-3 rounded-full bg-stone-50 dark:bg-stone-800",
        ),
        rx.el.div(
            rx.el.p(value, class_name="text-2xl font-bold text-stone-800 dark:text-stone-100"),
            rx.el.p(label, class_name="text-sm text-stone-500 dark:text-stone-400"),
        ),
        class_name="flex items-center gap-4 bg-white p-5 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700",
    )


def financial_summary_section() -> rx.Component:
    """Financial summary cards with income, expenses, profit."""
    return rx.el.div(
        rx.el.h3(
            "Financial Summary",
            class_name="text-lg font-semibold text-stone-800 mb-4 dark:text-stone-100",
        ),
        rx.el.div(
            summary_metric_card(
                "trending-up",
                "Total Income",
                "₹" + ReportsState.total_income.to_string(),
                "text-emerald-500",
            ),
            summary_metric_card(
                "trending-down",
                "Total Expenses",
                "₹" + ReportsState.total_expenses.to_string(),
                "text-red-500",
            ),
            summary_metric_card(
                "wallet",
                "Net Profit",
                "₹" + ReportsState.net_profit.to_string(),
                "text-blue-500",
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
        ),
    )


def expense_breakdown_section() -> rx.Component:
    """Expense breakdown by category."""
    return rx.el.div(
        rx.el.h3(
            "Expense Breakdown",
            class_name="text-lg font-semibold text-stone-800 mb-4 dark:text-stone-100",
        ),
        rx.el.div(
            rx.recharts.pie_chart(
                rx.recharts.graphing_tooltip(),
                rx.recharts.pie(
                    data=ReportsState.expense_by_category,
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    outer_radius=100,
                    inner_radius=60,
                    padding_angle=3,
                    stroke="#ffffff",
                    stroke_width=2,
                ),
                width="100%",
                height=300,
            ),
            rx.el.div(
                rx.foreach(
                    ReportsState.expense_by_category,
                    lambda item: rx.el.div(
                        rx.el.p(
                            item["name"],
                            class_name="font-medium text-stone-700 dark:text-stone-200",
                        ),
                        rx.el.p(
                            "₹" + item["value"].to_string(),
                            class_name="text-sm text-stone-500 dark:text-stone-400",
                        ),
                        class_name="flex items-center justify-between py-2 border-b border-stone-100 last:border-0 dark:border-stone-700",
                    ),
                ),
                class_name="w-full",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-6 bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700",
        ),
    )


def export_actions_section() -> rx.Component:
    """Export action buttons for PDF and Excel."""
    busy = ReportsState.is_generating
    return rx.el.div(
        rx.el.h3(
            "Export Reports",
            class_name="text-lg font-semibold text-stone-800 mb-4 dark:text-stone-100",
        ),
        rx.el.div(
            rx.el.button(
                rx.cond(
                    busy,
                    spinner(),
                    rx.icon("file-text", class_name="h-5 w-5 mr-2"),
                ),
                rx.cond(
                    busy,
                    "Generating…",
                    "Generate PDF Report",
                ),
                on_click=ReportsState.generate_pdf_report,
                disabled=busy,
                class_name="flex items-center min-h-[44px] bg-red-500 text-white px-6 py-3 rounded-xl font-semibold hover:bg-red-600 transition-all shadow-sm hover:shadow-md active:scale-[0.98] disabled:opacity-60 focus-visible:ring-2 focus-visible:ring-red-400",
            ),
            rx.el.button(
                rx.cond(
                    busy,
                    spinner(),
                    rx.icon("table", class_name="h-5 w-5 mr-2"),
                ),
                rx.cond(
                    busy,
                    "Generating…",
                    "Generate Excel Report",
                ),
                on_click=ReportsState.generate_excel_report,
                disabled=busy,
                class_name=f"flex items-center min-h-[44px] {BTN_PRIMARY} px-6 py-3 rounded-xl",
            ),
            class_name="flex gap-4 flex-wrap",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700",
    )


def reports_page_content() -> rx.Component:
    """The full reports page content."""
    return rx.el.div(
        date_range_selector(),
        rx.el.div(class_name="h-6"),
        financial_summary_section(),
        expense_breakdown_section(),
        rx.el.div(class_name="h-6"),
        export_actions_section(),
        class_name="max-w-6xl mx-auto",
    )


def reports_page() -> rx.Component:
    from app.components.layout import dashboard_layout

    return dashboard_layout(reports_page_content(), "Reports & Exports")

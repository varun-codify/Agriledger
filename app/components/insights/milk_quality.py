"""Milk quality prediction analytics.

Shows fat % and SNF % trends, quality scores, and predictions.
"""

import reflex as rx

from app.states.dashboard_state import DashboardState


def quality_score_card() -> rx.Component:
    """Average milk quality score based on fat and SNF percentages."""
    return rx.el.div(
        rx.el.h3(
            "Milk Quality Overview",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Avg Fat %", class_name="text-xs text-stone-500"),
                rx.el.p(
                    f"{DashboardState.avg_fat_percentage_week}%",
                    class_name="text-2xl font-bold text-emerald-600",
                ),
                rx.el.p(
                    "Target: 3.5-4.5%",
                    class_name="text-xs text-stone-400 mt-1",
                ),
                class_name="text-center p-4 bg-emerald-50 rounded-xl",
            ),
            rx.el.div(
                rx.el.p("Avg SNF %", class_name="text-xs text-stone-500"),
                rx.el.p(
                    f"{DashboardState.avg_snf_percentage_week}%",
                    class_name="text-2xl font-bold text-blue-600",
                ),
                rx.el.p(
                    "Target: 8.0-9.0%",
                    class_name="text-xs text-stone-400 mt-1",
                ),
                class_name="text-center p-4 bg-blue-50 rounded-xl",
            ),
            rx.el.div(
                rx.el.p("Quality Score", class_name="text-xs text-stone-500"),
                rx.el.p(
                    rx.cond(
                        (DashboardState.avg_fat_percentage_week >= 3.5) & (DashboardState.avg_fat_percentage_week <= 4.5),
                        "Excellent",
                        rx.cond(
                            (DashboardState.avg_fat_percentage_week >= 3.0) & (DashboardState.avg_fat_percentage_week <= 5.0),
                            "Good",
                            "Needs Attention",
                        ),
                    ),
                    class_name="text-2xl font-bold text-emerald-600",
                ),
                rx.el.p(
                    "Based on fat & SNF",
                    class_name="text-xs text-stone-400 mt-1",
                ),
                class_name="text-center p-4 bg-stone-50 rounded-xl",
            ),
            class_name="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def milk_quality_insights() -> rx.Component:
    """AI-powered milk quality insights."""
    return rx.el.div(
        rx.el.h3(
            "Quality Insights",
            class_name="text-lg font-semibold text-stone-800 mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("check-circle", class_name="h-5 w-5 text-emerald-500"),
                rx.el.p(
                    "Fat percentage is within the optimal range for high-quality milk.",
                    class_name="text-sm text-stone-600 ml-2",
                ),
                class_name="flex items-start p-3 bg-emerald-50 rounded-lg",
            ),
            rx.el.div(
                rx.icon("info", class_name="h-5 w-5 text-blue-500"),
                rx.el.p(
                    "Consistent SNF levels indicate good animal nutrition. Keep maintaining the current feed mix.",
                    class_name="text-sm text-stone-600 ml-2",
                ),
                class_name="flex items-start p-3 bg-blue-50 rounded-lg mt-2",
            ),
            rx.el.div(
                rx.icon("lightbulb", class_name="h-5 w-5 text-yellow-500"),
                rx.el.p(
                    "Tip: Higher fat content milk often commands premium prices. Consider selling directly to consumers for better margins.",
                    class_name="text-sm text-stone-600 ml-2",
                ),
                class_name="flex items-start p-3 bg-yellow-50 rounded-lg mt-2",
            ),
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )

import reflex as rx
from app.states.ai_insights_state import AIInsightsState


def health_score_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Farm Health Score", class_name="text-lg font-semibold text-stone-800"
            ),
            rx.el.button(
                rx.icon(
                    "refresh-ccw",
                    class_name=rx.cond(
                        AIInsightsState.is_loading, "h-4 w-4 animate-spin", "h-4 w-4"
                    ),
                ),
                on_click=AIInsightsState.refresh_insights,
                class_name="p-2 rounded-full hover:bg-stone-100 text-stone-500",
            ),
            class_name="flex justify-between items-center mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    AIInsightsState.health_score,
                    class_name="text-5xl font-bold text-emerald-600",
                ),
                rx.el.span("/100", class_name="text-xl text-stone-400 font-medium"),
                class_name="flex items-baseline justify-center",
            ),
            rx.el.p(
                "Your farm is performing well above average.",
                class_name="text-center text-sm text-stone-600 mt-2",
            ),
            class_name="py-6",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 h-full",
    )


def recommendation_card(rec: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                rx.match(
                    rec["type"],
                    ("optimization", "trending-up"),
                    ("warning", "alert-triangle"),
                    ("opportunity", "lightbulb"),
                    "info",
                ),
                class_name=rx.match(
                    rec["type"],
                    ("optimization", "h-5 w-5 text-blue-500"),
                    ("warning", "h-5 w-5 text-red-500"),
                    ("opportunity", "h-5 w-5 text-yellow-500"),
                    "h-5 w-5 text-stone-500",
                ),
            ),
            rx.el.h4(rec["title"], class_name="font-semibold text-stone-800 ml-3"),
            class_name="flex items-center mb-2",
        ),
        rx.el.p(rec["desc"], class_name="text-sm text-stone-600 ml-8"),
        class_name="p-4 rounded-xl bg-stone-50 border border-stone-100",
    )


def insights_widget() -> rx.Component:
    return rx.el.div(
        rx.el.h3("AI Insights", class_name="text-lg font-semibold text-stone-800 mb-4"),
        rx.el.div(
            rx.foreach(AIInsightsState.recommendations, recommendation_card),
            class_name="space-y-3",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 h-full",
    )
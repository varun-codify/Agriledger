"""Enhanced AI Insights page with conversational Q&A chatbot.

Provides a chat interface where farmers can ask questions about their farm data
and get AI-powered answers. Also shows health score, recommendations, and tips.
"""

import reflex as rx

from app.states.ai_insights_state import AIInsightsState


def health_score_card() -> rx.Component:
    """The farm health score gauge."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Farm Health Score", class_name="text-lg font-semibold text-stone-800 dark:text-stone-100"
            ),
            rx.el.button(
                rx.icon(
                    "refresh-ccw",
                    class_name=rx.cond(
                        AIInsightsState.is_loading,
                        "h-4 w-4 animate-spin",
                        "h-4 w-4",
                    ),
                ),
                on_click=AIInsightsState.refresh_insights,
                class_name="p-2 rounded-full hover:bg-stone-100 text-stone-500 dark:hover:bg-stone-700 dark:text-stone-400",
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
                rx.cond(
                    AIInsightsState.health_score >= 80,
                    "Your farm is performing well above average.",
                    rx.cond(
                        AIInsightsState.health_score >= 60,
                        "Your farm is doing okay. Check recommendations for improvements.",
                        "Your farm needs attention. Review the recommendations below.",
                    ),
                ),
                class_name="text-center text-sm text-stone-600 mt-2 dark:text-stone-300",
            ),
            # Score bar
            rx.el.div(
                rx.el.div(
                    class_name="h-2 rounded-full bg-emerald-500 transition-all duration-1000",
                    style={"width": AIInsightsState.health_score.to_string() + "%"},
                ),
                class_name="w-full h-2 bg-stone-200 rounded-full mt-4",
            ),
            class_name="py-6",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 h-full dark:bg-stone-900 dark:border-stone-700",
    )


def recommendation_card(rec: dict) -> rx.Component:
    """A single recommendation card."""
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
                    "h-5 w-5 text-stone-500 dark:text-stone-400",
                ),
            ),
            rx.el.h4(rec["title"], class_name="font-semibold text-stone-800 ml-3 dark:text-stone-100"),
            class_name="flex items-center mb-2",
        ),
        rx.el.p(rec["desc"], class_name="text-sm text-stone-600 ml-8 dark:text-stone-300"),
        class_name="p-4 rounded-xl bg-stone-50 dark:bg-stone-800 border border-stone-100",
    )


def insights_widget() -> rx.Component:
    """AI recommendations widget."""
    return rx.el.div(
        rx.el.h3(
            "AI Recommendations", class_name="text-lg font-semibold text-stone-800 mb-4 dark:text-stone-100"
        ),
        rx.el.div(
            rx.cond(
                AIInsightsState.is_loading,
                rx.el.div(
                    rx.el.div(class_name="h-16 bg-stone-100 rounded-xl animate-pulse"),
                    rx.el.div(class_name="h-16 bg-stone-100 rounded-xl animate-pulse mt-3"),
                    rx.el.div(class_name="h-16 bg-stone-100 rounded-xl animate-pulse mt-3"),
                    class_name="space-y-3",
                ),
                rx.el.div(
                    rx.foreach(
                        AIInsightsState.recommendations, recommendation_card
                    ),
                    class_name="space-y-3",
                ),
            ),
        ),
        rx.el.div(
            rx.el.h4(
                "Seasonal Tips",
                class_name="font-semibold text-stone-700 mt-6 dark:text-stone-200 mb-3",
            ),
            rx.el.ul(
                rx.foreach(
                    AIInsightsState.seasonal_tips,
                    lambda tip: rx.el.li(
                        rx.icon("circle-check", class_name="h-4 w-4 text-emerald-500 mr-2"),
                        rx.el.span(tip, class_name="text-sm text-stone-600 dark:text-stone-300"),
                        class_name="flex items-center py-1",
                    ),
                ),
                class_name="space-y-1",
            ),
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 h-full dark:bg-stone-900 dark:border-stone-700",
    )


def chat_message(message: dict) -> rx.Component:
    """A single chat message bubble."""
    is_user = message.get("role") == "user"
    return rx.el.div(
        rx.el.div(
            rx.icon(
                rx.cond(is_user, "user", "bot"),
                class_name="h-5 w-5",
            ),
            class_name=rx.cond(
                is_user,
                "w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center flex-shrink-0",
                "w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center flex-shrink-0",
            ),
        ),
        rx.el.div(
            message.get("content", ""),
            class_name=rx.cond(
                is_user,
                "bg-emerald-500 text-white px-4 py-3 rounded-2xl rounded-tr-sm text-sm max-w-md",
                "bg-stone-100 text-stone-800 dark:bg-stone-800 dark:text-stone-100 px-4 py-3 rounded-2xl rounded-tl-sm text-sm max-w-md",
            ),
        ),
        class_name=rx.cond(
            is_user,
            "flex items-end gap-2 justify-end mb-3",
            "flex items-end gap-2 justify-start mb-3",
        ),
    )


def ai_chatbot_section() -> rx.Component:
    """The AI conversational Q&A chatbot interface."""
    return rx.el.div(
        rx.el.div(
            rx.icon("brain-circuit", class_name="h-6 w-6 text-emerald-500"),
            rx.el.h3(
                "Ask AgriLedger AI",
                class_name="text-lg font-semibold text-stone-800 dark:text-stone-100",
            ),
            class_name="flex items-center gap-2 mb-4",
        ),
        # Chat messages area
        rx.el.div(
            rx.cond(
                AIInsightsState.chat_messages.length() == 0,
                rx.el.div(
                    rx.el.p(
                        "Ask me anything about your farm!",
                        class_name="text-stone-400 text-center dark:text-stone-500",
                    ),
                    rx.el.div(
                        rx.foreach(
                            [
                                "Why did milk production drop?",
                                "How can I reduce feed costs?",
                                "What crops should I plant next?",
                                "How is my breeding success rate?",
                            ],
                            lambda q: rx.el.button(
                                q,
                                on_click=lambda: AIInsightsState.ask_question(q),
                                class_name="text-left text-xs text-emerald-600 bg-emerald-50 px-3 py-2 rounded-lg hover:bg-emerald-100 transition",
                            ),
                        ),
                        class_name="flex flex-wrap gap-2 mt-4 justify-center",
                    ),
                    class_name="py-8",
                ),
                rx.el.div(
                    rx.foreach(AIInsightsState.chat_messages, chat_message),
                    class_name="space-y-1 max-h-96 overflow-y-auto p-2",
                ),
            ),
            class_name="bg-stone-50 rounded-xl p-4 dark:bg-stone-800 min-h-[200px] mb-4",
        ),
        # Input area
        rx.el.div(
            rx.el.input(
                placeholder="Ask about your farm...",
                value=AIInsightsState.chat_input,
                on_change=AIInsightsState.set_chat_input,
                on_key_down=AIInsightsState.handle_chat_key,
                class_name="flex-1 px-4 py-3 rounded-xl border border-stone-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition text-sm",
            ),
            rx.el.button(
                rx.icon("send", class_name="h-4 w-4"),
                on_click=AIInsightsState.send_chat_message,
                class_name="p-3 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-all",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700",
    )

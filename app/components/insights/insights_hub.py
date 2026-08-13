"""Consolidated Insights & AI page.

Combines the weather / farming-suggestions view (Farm Insights) and the
AI health score / chatbot (AI Assistant) under two tabs on one route.
"""

import reflex as rx

from app.components.common import segmented_control
from app.components.crops.farm_insights import farm_insights_page
from app.components.insights.ai_insights import (
    ai_chatbot_section,
    health_score_card,
    insights_widget,
)
from app.states.ai_insights_state import AIInsightsState
from app.states.ui_state import UIState


def _switch_tab(tab: str):
    """Set the active tab, refreshing AI data when the AI tab is opened."""
    events = [UIState.set_insights_tab(tab)]
    if tab == "ai":
        events.append(AIInsightsState.refresh_insights())
    return events


def insights_hub_page() -> rx.Component:
    """The full Insights & AI page (weather | AI assistant tabs)."""
    from app.components.layout import dashboard_layout

    return dashboard_layout(
        rx.el.div(
            segmented_control(
                UIState.insights_tab,
                [
                    ("weather", "Farm Insights", "cloud-sun"),
                    ("ai", "AI Assistant", "bot"),
                ],
                _switch_tab,
            ),
            rx.cond(
                UIState.insights_tab == "weather",
                farm_insights_page(),
                rx.el.div(
                    rx.el.div(
                        health_score_card(),
                        insights_widget(),
                        class_name="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6",
                    ),
                    ai_chatbot_section(),
                ),
            ),
            class_name="max-w-7xl mx-auto",
        ),
        "Insights & AI",
    )

"""Feed Intelligence pages.

- ``Operations`` tab — daily operations: overview cards, daily feeding,
  inventory (incl. crops→feed stock), feeding plans, AI advisor, reports.
- ``Analytics`` tab — charts and intelligence: consumption stats, trends,
  milk-vs-feed, efficiency, purchase planner, smart alerts.

Both views live on the single ``/feed`` route, switched via tabs.
"""

import reflex as rx

from app.components.feed import dialogs, feed_panels
from app.states.feed_state import FeedState

FEED_QUICK_NAV = [
    ("feed-overview", "Overview"),
    ("feed-feeding", "Daily Feeding"),
    ("feed-inventory", "Inventory"),
    ("feed-plans", "Plans"),
    ("feed-ration", "Ration"),
    ("feed-advisor", "AI Advisor"),
    ("feed-simulator", "Simulator"),
    ("feed-reports", "Reports"),
]

ANALYTICS_QUICK_NAV = [
    ("feed-stats", "Overview"),
    ("feed-trends", "Trends"),
    ("feed-milkfeed", "Milk vs Feed"),
    ("feed-efficiency", "Efficiency"),
    ("feed-planner", "Planner"),
    ("feed-alerts", "Alerts"),
]


def nav_pill(item: rx.Var) -> rx.Component:
    return rx.el.a(
        item[1],
        href="#" + item[0],
        on_click=lambda: FeedState.set_active_section(item[0]),
        class_name=rx.cond(
            FeedState.active_section == item[0],
            "flex-shrink-0 px-4 py-2 rounded-full bg-emerald-500 text-white text-sm font-semibold transition-all",
            "flex-shrink-0 px-4 py-2 rounded-full bg-stone-100 text-stone-600 dark:bg-stone-800 dark:text-stone-300 text-sm font-semibold hover:bg-emerald-100 hover:text-emerald-700 transition-all",
        ),
    )


def quick_nav(items: list, extra: rx.Component | None = None) -> rx.Component:
    return rx.el.div(
        rx.foreach(items, nav_pill),
        extra,
        class_name="sticky top-0 z-20 flex flex-wrap items-center gap-2 bg-white/90 backdrop-blur p-3 rounded-2xl border border-stone-100 dark:bg-stone-900/90 dark:border-stone-700 shadow-sm mb-6",
    )


def feed_view_tabs() -> rx.Component:
    """Top-level tab bar: Operations vs Analytics."""
    return rx.el.div(
        rx.el.button(
            rx.icon("clipboard-list", class_name="h-4 w-4 mr-2"),
            "Operations",
            on_click=lambda: FeedState.switch_view("operations"),
            class_name=rx.cond(
                FeedState.active_view == "operations",
                "flex items-center px-5 py-2.5 rounded-xl bg-emerald-500 text-white font-semibold text-sm transition-all",
                "flex items-center px-5 py-2.5 rounded-xl bg-white text-stone-600 font-semibold text-sm border border-stone-200 hover:bg-stone-50 dark:bg-stone-800 dark:text-stone-300 dark:border-stone-600 dark:hover:bg-stone-700 transition-all",
            ),
        ),
        rx.el.button(
            rx.icon("chart-column", class_name="h-4 w-4 mr-2"),
            "Analytics",
            on_click=lambda: FeedState.switch_view("analytics"),
            class_name=rx.cond(
                FeedState.active_view == "analytics",
                "flex items-center px-5 py-2.5 rounded-xl bg-emerald-500 text-white font-semibold text-sm transition-all",
                "flex items-center px-5 py-2.5 rounded-xl bg-white text-stone-600 font-semibold text-sm border border-stone-200 hover:bg-stone-50 dark:bg-stone-800 dark:text-stone-300 dark:border-stone-600 dark:hover:bg-stone-700 transition-all",
            ),
        ),
        class_name="flex gap-2 mb-6",
    )


def analytics_pill() -> rx.Component:
    return rx.el.button(
        "Analytics →",
        on_click=lambda: FeedState.switch_view("analytics"),
        class_name="flex-shrink-0 px-4 py-2 rounded-full bg-emerald-500 text-white text-sm font-semibold hover:bg-emerald-600 transition-all",
    )


def feed_operations_view() -> rx.Component:
    """Daily feeding operations (overview, feeding, inventory, plans, AI)."""
    return rx.el.div(
        quick_nav(FEED_QUICK_NAV, analytics_pill()),
        feed_panels.feed_overview_cards(),
        rx.el.div(feed_panels.daily_feeding_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.inventory_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.feeding_plans_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.ration_optimizer_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.feed_advisor_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.feed_simulator_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.feed_reports_panel(), class_name="mt-6"),
    )


def feed_analytics_view() -> rx.Component:
    """Feed charts and intelligence (stats, trends, efficiency, planner)."""
    return rx.el.div(
        quick_nav(ANALYTICS_QUICK_NAV),
        feed_panels.analytics_stats_panel(),
        rx.el.div(feed_panels.feed_trends_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.milk_feed_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.efficiency_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.purchase_planner_panel(), class_name="mt-6"),
        rx.el.div(feed_panels.smart_alerts_panel(), class_name="mt-6"),
    )


def feed_page() -> rx.Component:
    return rx.el.div(
        feed_view_tabs(),
        rx.cond(
            FeedState.active_view == "operations",
            feed_operations_view(),
            feed_analytics_view(),
        ),
        dialogs.feed_type_dialog(),
        dialogs.stock_dialog(),
        dialogs.plan_dialog(),
        on_mount=lambda: FeedState.switch_view("operations"),
    )

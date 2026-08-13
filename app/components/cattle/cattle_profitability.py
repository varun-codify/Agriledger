"""Cattle profitability per animal — displays pre-computed profit data."""

import reflex as rx

from app.states.cattle_state import CattleState


def profitability_card(item: rx.Var[dict]) -> rx.Component:
    """Display profitability metrics for a single animal using reactive Vars."""
    return rx.el.div(
        rx.el.div(
            rx.image(
                src=item["image_url"],
                class_name="w-10 h-10 rounded-full object-cover",
            ),
            rx.el.div(
                rx.el.p(item["name"], class_name="font-semibold text-stone-800 text-sm"),
                rx.el.p(item["animal_type"], class_name="text-xs text-stone-500 capitalize"),
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Milk (L)", class_name="text-xs text-stone-500"),
                rx.el.p(item["total_milk"], class_name="text-sm font-bold text-stone-800"),
            ),
            rx.el.div(
                rx.el.p("Revenue", class_name="text-xs text-stone-500"),
                rx.el.p(item["revenue"], class_name="text-sm font-bold text-emerald-600"),
            ),
            rx.el.div(
                rx.el.p("Cost", class_name="text-xs text-stone-500"),
                rx.el.p(item["cost"], class_name="text-sm font-bold text-red-500"),
            ),
            rx.el.div(
                rx.el.p("Profit", class_name="text-xs text-stone-500"),
                rx.el.p(
                    item["profit"],
                    class_name=rx.cond(
                        item["profit_positive"],
                        "text-sm font-bold text-emerald-600",
                        "text-sm font-bold text-red-600",
                    ),
                ),
            ),
            class_name="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-3",
        ),
        class_name="bg-white p-4 rounded-xl shadow-sm border border-stone-100",
    )


def cattle_profitability_section() -> rx.Component:
    """Section showing profitability per animal."""
    return rx.el.div(
        rx.el.h3(
            "Animal Profitability",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.el.div(
            rx.foreach(
                CattleState.cattle_profitability_data,
                lambda item: profitability_card(item),
            ),
            class_name="space-y-3",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )

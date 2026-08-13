import reflex as rx

from app.states.transaction_state import TransactionState


def category_card(category: dict) -> rx.Component:
    is_selected = TransactionState.selected_category["name"] == category["name"]
    return rx.el.div(
        rx.icon(category["icon"], class_name="h-8 w-8 mx-auto mb-2 text-stone-600"),
        rx.el.p(category["name"], class_name="text-sm font-medium text-center"),
        on_click=lambda: TransactionState.set_category(category),
        class_name=rx.cond(
            is_selected,
            "p-4 rounded-xl border-2 border-emerald-500 bg-emerald-50 text-emerald-800 cursor-pointer transform scale-105 shadow-md transition-all",
            "p-4 rounded-xl border border-stone-200 bg-white text-stone-700 cursor-pointer hover:shadow-sm hover:border-stone-300 transition-all",
        ),
    )


def step_2_category() -> rx.Component:
    """Wizard step 2: Select transaction category."""
    return rx.el.div(
        rx.el.h2(
            "Select a Category",
            class_name="text-2xl font-bold text-stone-800 text-center mb-8",
        ),
        rx.el.div(
            rx.foreach(TransactionState.current_categories, category_card),
            class_name="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 gap-4",
        ),
        class_name="w-full",
    )

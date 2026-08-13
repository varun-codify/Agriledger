import reflex as rx

from app.states.transaction_state import TransactionState


def type_selection_card(type: str, icon: str, description: str) -> rx.Component:
    is_selected = TransactionState.transaction_type == type
    return rx.el.div(
        rx.icon(icon, class_name="h-10 w-10 mb-3"),
        rx.el.h3(type.capitalize(), class_name="text-xl font-semibold"),
        rx.el.p(description, class_name="text-sm text-stone-500 mt-1"),
        on_click=lambda: TransactionState.set_transaction_type(type),
        class_name=rx.cond(
            is_selected,
            "p-6 rounded-2xl border-2 border-emerald-500 bg-emerald-50 text-emerald-800 cursor-pointer text-center transform scale-105 shadow-lg transition-all",
            "p-6 rounded-2xl border border-stone-200 bg-white text-stone-700 cursor-pointer text-center hover:shadow-md hover:border-stone-300 transition-all",
        ),
    )


def step_1_type() -> rx.Component:
    """Wizard step 1: Select transaction type (Income/Expense)."""
    return rx.el.div(
        rx.el.h2(
            "What kind of transaction is this?",
            class_name="text-2xl font-bold text-stone-800 text-center mb-8",
        ),
        rx.el.div(
            type_selection_card("income", "trending-up", "Money earned"),
            type_selection_card("expense", "trending-down", "Money spent"),
            class_name="grid md:grid-cols-2 gap-6",
        ),
        class_name="w-full",
    )

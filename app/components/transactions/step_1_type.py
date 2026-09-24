import reflex as rx

from app.states.transaction_state import TransactionState


def type_selection_card(type: str, icon: str, description: str) -> rx.Component:
    is_selected = TransactionState.transaction_type == type
    is_income = type == "income"

    card_style = rx.cond(
        is_selected,
        rx.cond(
            is_income,
            "p-6 rounded-2xl border-2 border-emerald-500 bg-emerald-100/90 text-emerald-950 cursor-pointer text-center transform scale-105 shadow-lg transition-all",
            "p-6 rounded-2xl border-2 border-rose-500 bg-rose-100/90 text-rose-950 cursor-pointer text-center transform scale-105 shadow-lg transition-all",
        ),
        rx.cond(
            is_income,
            "p-6 rounded-2xl border border-emerald-200/90 bg-emerald-50/70 text-emerald-900 cursor-pointer text-center hover:bg-emerald-100/80 hover:border-emerald-300 hover:shadow-md transition-all",
            "p-6 rounded-2xl border border-rose-200/90 bg-rose-50/70 text-rose-900 cursor-pointer text-center hover:bg-rose-100/80 hover:border-rose-300 hover:shadow-md transition-all",
        ),
    )

    icon_style = rx.cond(
        is_income,
        "h-10 w-10 mb-3 mx-auto text-emerald-600",
        "h-10 w-10 mb-3 mx-auto text-rose-600",
    )

    subtext_style = rx.cond(
        is_income,
        "text-sm text-emerald-700/90 mt-1 font-medium",
        "text-sm text-rose-700/90 mt-1 font-medium",
    )

    return rx.el.div(
        rx.icon(icon, class_name=icon_style),
        rx.el.h3(type.capitalize(), class_name="text-xl font-bold tracking-tight"),
        rx.el.p(description, class_name=subtext_style),
        on_click=lambda: TransactionState.set_transaction_type(type),
        class_name=card_style,
    )


def step_1_type() -> rx.Component:
    """Wizard step 1: Select transaction type (Income/Expense)."""
    return rx.el.div(
        rx.el.h2(
            "What kind of transaction is this?",
            class_name="text-2xl font-bold text-stone-800 text-center mb-8 dark:text-stone-100",
        ),
        rx.el.div(
            type_selection_card("income", "trending-up", "Money earned"),
            type_selection_card("expense", "trending-down", "Money spent"),
            class_name="grid md:grid-cols-2 gap-6",
        ),
        class_name="w-full",
    )

import reflex as rx
from app.states.transaction_state import TransactionState
import datetime


def date_quick_button(label: str, days_offset: int) -> rx.Component:
    date_val = (
        datetime.date.today() + datetime.timedelta(days=days_offset)
    ).isoformat()
    is_selected = TransactionState.date == date_val
    return rx.el.button(
        label,
        on_click=lambda: TransactionState.set_date(date_val),
        class_name=rx.cond(
            is_selected,
            "px-6 py-2 rounded-lg bg-emerald-500 text-white font-semibold transition",
            "px-6 py-2 rounded-lg bg-stone-100 text-stone-700 font-semibold hover:bg-stone-200 transition",
        ),
    )


def step_4_date() -> rx.Component:
    """Wizard step 4: Select the date."""
    return rx.el.div(
        rx.el.h2(
            "When did this transaction happen?",
            class_name="text-2xl font-bold text-stone-800 text-center mb-8",
        ),
        rx.el.div(
            date_quick_button("Today", 0),
            date_quick_button("Yesterday", -1),
            class_name="flex items-center justify-center gap-4 mb-6",
        ),
        rx.el.div(
            rx.el.input(
                type="date",
                default_value=TransactionState.date,
                on_change=TransactionState.set_date,
                class_name="w-full max-w-sm mx-auto px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 transition text-center font-semibold text-lg",
            ),
            class_name="flex justify-center",
        ),
        class_name="w-full",
    )
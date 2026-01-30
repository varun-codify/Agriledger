import reflex as rx
from app.states.transaction_state import TransactionState


def step_5_notes() -> rx.Component:
    """Wizard step 5: Add optional notes."""
    return rx.el.div(
        rx.el.h2(
            "Any additional notes?",
            class_name="text-2xl font-bold text-stone-800 text-center mb-8",
        ),
        rx.el.p(
            "(Optional)", class_name="text-sm text-stone-500 text-center -mt-6 mb-8"
        ),
        rx.el.textarea(
            placeholder="E.g., Bought from John's store, for cow #12...",
            default_value=TransactionState.notes,
            on_change=TransactionState.set_notes,
            class_name="w-full h-32 px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 transition",
        ),
        class_name="w-full max-w-md mx-auto",
    )
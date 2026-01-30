import reflex as rx
from app.states.transaction_state import TransactionState


def review_item(label: str, value: rx.Var, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-5 w-5 text-stone-500"),
            rx.el.p(label, class_name="font-medium text-stone-600"),
            class_name="flex items-center gap-3",
        ),
        rx.el.p(value, class_name="font-semibold text-stone-800 text-right"),
        class_name="flex items-center justify-between py-3 border-b border-stone-100",
    )


def step_6_review() -> rx.Component:
    """Wizard step 6: Review and submit the transaction."""
    return rx.el.div(
        rx.el.h2(
            "Review Your Transaction",
            class_name="text-2xl font-bold text-stone-800 text-center mb-6",
        ),
        rx.el.div(
            review_item("Type", TransactionState.transaction_type.capitalize(), "tag"),
            review_item(
                "Category",
                TransactionState.selected_category["name"],
                TransactionState.selected_category["icon"],
            ),
            review_item("Amount", "$" + TransactionState.amount_str, "dollar-sign"),
            review_item("Date", TransactionState.date, "calendar-days"),
            review_item(
                "Notes",
                rx.cond(TransactionState.notes, TransactionState.notes, "-"),
                "sticky-note",
            ),
            class_name="space-y-2",
        ),
        class_name="w-full max-w-md mx-auto",
    )
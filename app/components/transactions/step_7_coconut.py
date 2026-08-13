import reflex as rx

from app.states.transaction_state import TransactionState


def coconut_field(
    label: str,
    placeholder: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    input_type: str = "text",
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-stone-700 mb-1"),
        rx.el.input(
            type=input_type,
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition",
        ),
    )


def step_7_coconut() -> rx.Component:
    """Wizard step 7: Coconut sale details (auto-calculated total)."""
    return rx.el.div(
        rx.el.h2(
            "Coconut Sale Details",
            class_name="text-2xl font-bold text-stone-800 text-center mb-8",
        ),
        rx.el.div(
            coconut_field(
                "Number of Coconuts",
                "e.g., 100",
                TransactionState.coconut_count.to_string(),
                TransactionState.set_coconut_count,
                input_type="number",
            ),
            coconut_field(
                "Price per Coconut (₹)",
                "e.g., 1.5",
                TransactionState.price_per_coconut.to_string(),
                TransactionState.set_price_per_coconut,
                input_type="number",
            ),
            coconut_field(
                "Buyer (optional)",
                "Buyer name",
                TransactionState.buyer,
                TransactionState.set_buyer,
            ),
            coconut_field(
                "Date",
                "",
                TransactionState.date,
                TransactionState.set_date,
                input_type="date",
            ),
            rx.el.div(
                rx.el.p("Total Amount", class_name="text-sm text-stone-500"),
                rx.el.p(
                    "₹" + TransactionState.coconut_total_amount.to_string(),
                    class_name="text-3xl font-bold text-emerald-600",
                ),
                class_name="text-center bg-emerald-50 rounded-xl p-4",
            ),
            class_name="space-y-4 max-w-md mx-auto",
        ),
        class_name="w-full",
    )

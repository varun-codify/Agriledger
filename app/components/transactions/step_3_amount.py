import reflex as rx

from app.states.transaction_state import TransactionState


def keypad_button(key: str) -> rx.Component:
    return rx.el.button(
        key,
        on_click=lambda: TransactionState.handle_keypad(key),
        class_name="p-4 rounded-lg bg-stone-100 text-stone-800 font-bold text-2xl hover:bg-stone-200 transition",
    )


def quick_amount_button(value: int) -> rx.Component:
    return rx.el.button(
        f"{('+' if value > 0 else '')}{value}",
        on_click=lambda: TransactionState.modify_amount(value),
        class_name="px-3 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 hover:bg-emerald-200 transition",
    )


def step_3_amount() -> rx.Component:
    """Wizard step 3: Enter the amount."""
    return rx.el.div(
        rx.el.h2(
            "Enter the Amount",
            class_name="text-2xl font-bold text-stone-800 text-center mb-4",
        ),
        rx.el.div(
            rx.el.span("₹", class_name="text-4xl font-bold text-stone-400"),
            rx.el.p(
                TransactionState.amount_str,
                class_name="text-6xl font-bold text-stone-800",
            ),
            class_name="flex items-center justify-center gap-2 mb-4",
        ),
        rx.el.div(
            quick_amount_button(100),
            quick_amount_button(500),
            quick_amount_button(1000),
            quick_amount_button(-100),
            quick_amount_button(-500),
            class_name="flex items-center justify-center gap-2 mb-6",
        ),
        rx.el.div(
            keypad_button("1"),
            keypad_button("2"),
            keypad_button("3"),
            keypad_button("4"),
            keypad_button("5"),
            keypad_button("6"),
            keypad_button("7"),
            keypad_button("8"),
            keypad_button("9"),
            keypad_button("."),
            keypad_button("0"),
            rx.el.button(
                rx.icon("delete", class_name="h-8 w-8"),
                on_click=lambda: TransactionState.handle_keypad("del"),
                class_name="p-4 rounded-lg bg-red-100 text-red-600 font-bold text-2xl hover:bg-red-200 transition",
            ),
            class_name="grid grid-cols-3 gap-2 max-w-xs mx-auto",
        ),
        class_name="w-full",
    )

import reflex as rx

from app.states.transaction_state import TransactionState


def quick_add_dialog() -> rx.Component:
    """A dialog for quick transaction entry."""
    return rx.el.div(
        rx.el.button(
            rx.icon("plus", class_name="h-7 w-7"),
            on_click=lambda: TransactionState.toggle_quick_add(True),
            class_name="fixed bottom-24 right-4 md:bottom-6 md:right-6 bg-emerald-500 text-white p-4 rounded-full shadow-lg hover:bg-emerald-600 transition-transform hover:scale-105 z-30",
        ),
        rx.cond(
            TransactionState.show_quick_add,
            rx.el.div(
                rx.el.div(
                    on_click=lambda: TransactionState.toggle_quick_add(False),
                    class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Quick Add", class_name="text-xl font-bold text-stone-800"
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5"),
                            on_click=lambda: TransactionState.toggle_quick_add(False),
                            class_name="p-1 rounded-full hover:bg-stone-200",
                        ),
                        class_name="flex items-center justify-between mb-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Income",
                            on_click=lambda: TransactionState.quick_add_set_type(
                                "income"
                            ),
                            class_name=rx.cond(
                                TransactionState.transaction_type == "income",
                                "w-full py-2 rounded-lg bg-emerald-500 text-white font-semibold",
                                "w-full py-2 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                            ),
                        ),
                        rx.el.button(
                            "Expense",
                            on_click=lambda: TransactionState.quick_add_set_type(
                                "expense"
                            ),
                            class_name=rx.cond(
                                TransactionState.transaction_type == "expense",
                                "w-full py-2 rounded-lg bg-red-500 text-white font-semibold",
                                "w-full py-2 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                            ),
                        ),
                        class_name="grid grid-cols-2 gap-2 mb-4",
                    ),
                    rx.el.div(
                        rx.el.span("₹", class_name="text-2xl font-bold text-stone-400"),
                        rx.el.p(
                            TransactionState.amount_str,
                            class_name="text-4xl font-bold text-stone-800",
                        ),
                        class_name="flex items-center justify-center gap-1 mb-4 text-center",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "1",
                            on_click=lambda: TransactionState.handle_keypad("1"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            "2",
                            on_click=lambda: TransactionState.handle_keypad("2"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            "3",
                            on_click=lambda: TransactionState.handle_keypad("3"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            "4",
                            on_click=lambda: TransactionState.handle_keypad("4"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            "5",
                            on_click=lambda: TransactionState.handle_keypad("5"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            "6",
                            on_click=lambda: TransactionState.handle_keypad("6"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            "7",
                            on_click=lambda: TransactionState.handle_keypad("7"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            "8",
                            on_click=lambda: TransactionState.handle_keypad("8"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            "9",
                            on_click=lambda: TransactionState.handle_keypad("9"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            ".",
                            on_click=lambda: TransactionState.handle_keypad("."),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            "0",
                            on_click=lambda: TransactionState.handle_keypad("0"),
                            class_name="p-3 rounded-lg bg-stone-100 text-stone-700 font-semibold",
                        ),
                        rx.el.button(
                            rx.icon("delete"),
                            on_click=lambda: TransactionState.handle_keypad("del"),
                            class_name="p-3 rounded-lg bg-red-100 text-red-500",
                        ),
                        class_name="grid grid-cols-3 gap-2 mb-4",
                    ),
                    rx.el.h3(
                        "Category",
                        class_name="text-md font-semibold text-stone-700 mb-2",
                    ),
                    rx.el.div(
                        rx.foreach(
                            TransactionState.current_categories[:5],
                            lambda cat: rx.el.button(
                                rx.icon(cat["icon"], class_name="h-5 w-5 mr-2"),
                                cat["name"],
                                on_click=lambda: TransactionState.quick_add_set_category(
                                    cat
                                ),
                                class_name=rx.cond(
                                    TransactionState.selected_category["name"]
                                    == cat["name"],
                                    "flex items-center text-xs p-2 rounded-lg bg-emerald-100 text-emerald-800",
                                    "flex items-center text-xs p-2 rounded-lg bg-stone-100 text-stone-700",
                                ),
                            ),
                        ),
                        class_name="flex flex-wrap gap-2 mb-6",
                    ),
                    rx.el.button(
                        "Add Transaction",
                        on_click=TransactionState.quick_add_transaction,
                        class_name="w-full py-3 bg-emerald-500 text-white font-bold rounded-lg hover:bg-emerald-600 transition",
                    ),
                    class_name="fixed bottom-0 left-0 right-0 md:bottom-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 bg-white rounded-t-2xl md:rounded-2xl shadow-2xl p-6 w-full max-w-sm z-50",
                ),
            ),
        ),
    )

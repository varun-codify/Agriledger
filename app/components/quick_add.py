import reflex as rx

from app.components.common import BTN_PRIMARY
from app.states.transaction_state import TransactionState


def _keypad_key(label: str) -> rx.Component:
    return rx.el.button(
        label,
        on_click=lambda: TransactionState.handle_keypad(label),
        class_name="p-3 rounded-lg bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-200 font-semibold transition-all hover:bg-stone-200 dark:hover:bg-stone-700 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/50",
    )


def quick_add_dialog() -> rx.Component:
    """A dialog for quick transaction entry."""
    return rx.el.div(
        rx.el.button(
            rx.icon("plus", class_name="h-7 w-7"),
            on_click=lambda: TransactionState.toggle_quick_add(True),
            class_name="fixed bottom-24 right-4 md:bottom-6 md:right-6 bg-emerald-500 text-white p-4 rounded-full shadow-lg hover:bg-emerald-600 transition-all hover:scale-110 active:scale-95 z-30 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-emerald-400/50",
        ),
        rx.cond(
            TransactionState.show_quick_add,
            rx.el.div(
                rx.el.div(
                    on_click=lambda: TransactionState.toggle_quick_add(False),
                    class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 al-fade-in",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Quick Add",
                            class_name="text-xl font-bold text-stone-800 dark:text-stone-100",
                        ),
                        rx.el.button(
                            rx.icon("x", class_name="h-5 w-5"),
                            on_click=lambda: TransactionState.toggle_quick_add(False),
                            class_name="p-1 rounded-full hover:bg-stone-200 transition-all active:scale-90 dark:hover:bg-stone-700",
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
                                "w-full py-2 rounded-lg bg-emerald-500 text-white font-semibold shadow-sm transition-all active:scale-[0.98]",
                                "w-full py-2 rounded-lg bg-emerald-50/80 text-emerald-800 border border-emerald-200 font-semibold hover:bg-emerald-100/80 transition-all active:scale-[0.98] dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-900",
                            ),
                        ),
                        rx.el.button(
                            "Expense",
                            on_click=lambda: TransactionState.quick_add_set_type(
                                "expense"
                            ),
                            class_name=rx.cond(
                                TransactionState.transaction_type == "expense",
                                "w-full py-2 rounded-lg bg-rose-500 text-white font-semibold shadow-sm transition-all active:scale-[0.98]",
                                "w-full py-2 rounded-lg bg-rose-50/80 text-rose-800 border border-rose-200 font-semibold hover:bg-rose-100/80 transition-all active:scale-[0.98] dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-900",
                            ),
                        ),
                        class_name="grid grid-cols-2 gap-2 mb-4",
                    ),
                    rx.el.div(
                        rx.el.span(
                            "₹",
                            class_name="text-2xl font-bold text-stone-400 dark:text-stone-500",
                        ),
                        rx.el.p(
                            TransactionState.amount_str,
                            class_name="text-4xl font-bold text-stone-800 dark:text-stone-100",
                        ),
                        class_name="flex items-center justify-center gap-1 mb-4 text-center",
                    ),
                    rx.el.div(
                        [_keypad_key(k) for k in ["1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "0"]],
                        rx.el.button(
                            rx.icon("delete"),
                            on_click=lambda: TransactionState.handle_keypad("del"),
                            class_name="p-3 rounded-lg bg-red-100 dark:bg-red-950 text-red-500 font-semibold transition-all hover:bg-red-200 dark:hover:bg-red-900 active:scale-95",
                        ),
                        class_name="grid grid-cols-3 gap-2 mb-4",
                    ),
                    rx.el.h3(
                        "Category",
                        class_name="text-md font-semibold text-stone-700 mb-2 dark:text-stone-200",
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
                                    "flex items-center text-xs p-2 rounded-lg bg-emerald-100 text-emerald-800 transition-all active:scale-95 dark:bg-emerald-950 dark:text-emerald-300",
                                    "flex items-center text-xs p-2 rounded-lg bg-stone-100 text-stone-700 transition-all hover:bg-stone-200 active:scale-95 dark:bg-stone-800 dark:text-stone-300 dark:hover:bg-stone-700",
                                ),
                            ),
                        ),
                        class_name="flex flex-wrap gap-2 mb-6",
                    ),
                    rx.el.button(
                        "Add Transaction",
                        on_click=TransactionState.quick_add_transaction,
                        class_name=f"w-full py-3 {BTN_PRIMARY}",
                    ),
                    class_name="al-modal-in fixed bottom-0 left-0 right-0 md:bottom-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 bg-white dark:bg-stone-900 rounded-t-2xl md:rounded-2xl shadow-2xl p-6 w-full max-w-sm z-50 border border-stone-100 dark:border-stone-700",
                ),
            ),
        ),
    )

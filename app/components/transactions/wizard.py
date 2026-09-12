import reflex as rx

from app.states.transaction_state import TransactionState

from .step_1_type import step_1_type
from .step_2_category import step_2_category
from .step_3_amount import step_3_amount
from .step_4_date import step_4_date
from .step_5_notes import step_5_notes
from .step_6_review import step_6_review
from .step_7_coconut import step_7_coconut
from .step_8_milk import step_8_milk


def wizard_progress() -> rx.Component:
    return rx.el.div(
        rx.foreach(
            TransactionState.wizard_steps,
            lambda step, index: rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.cond(
                            TransactionState.current_step > index + 1,
                            rx.icon("check", class_name="h-4 w-4 text-white"),
                            rx.el.span(index + 1, class_name="text-xs font-semibold"),
                        ),
                        class_name=rx.cond(
                            TransactionState.current_step > index,
                            "flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500 text-white",
                            "flex items-center justify-center w-6 h-6 rounded-full bg-stone-200 text-stone-600",
                        ),
                    ),
                    rx.el.p(
                        step,
                        class_name=rx.cond(
                            TransactionState.current_step > index,
                            "text-xs font-semibold text-emerald-600 mt-1 hidden sm:block",
                            "text-xs font-medium text-stone-500 mt-1 hidden sm:block",
                        ),
                    ),
                    class_name="flex flex-col items-center",
                ),
                rx.cond(
                    index < TransactionState.wizard_steps.length() - 1,
                    rx.el.div(
                        class_name=rx.cond(
                            TransactionState.current_step > index + 1,
                            "flex-1 h-0.5 bg-emerald-500",
                            "flex-1 h-0.5 bg-stone-200",
                        )
                    ),
                    None,
                ),
                class_name="flex-1 flex items-center",
            ),
        ),
        class_name="flex items-center w-full max-w-2xl mx-auto mb-8",
    )


def wizard_nav() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            "Back",
            on_click=TransactionState.prev_step,
            class_name="bg-stone-200 text-stone-700 px-6 py-2 rounded-lg font-semibold hover:bg-stone-300 transition",
            disabled=TransactionState.current_step == 1,
        ),
        rx.cond(
            TransactionState.current_step >= 6,
            rx.el.button(
                "Submit Transaction",
                on_click=TransactionState.submit_transaction,
                class_name="bg-emerald-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-emerald-600 transition",
            ),
            rx.el.button(
                "Next",
                on_click=TransactionState.next_step,
                class_name="bg-emerald-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-emerald-600 transition",
                disabled=rx.cond(
                    (TransactionState.current_step == 1)
                    & (TransactionState.transaction_type == None),  # noqa: E711 — rx.cond compiles to JS equality
                    True,
                    rx.cond(
                        (TransactionState.current_step == 2)
                        & (TransactionState.selected_category == None),  # noqa: E711
                        True,
                        rx.cond(
                            (TransactionState.current_step == 3)
                            & (TransactionState.amount <= 0),
                            True,
                            False,
                        ),
                    ),
                ),
            ),
        ),
        class_name="flex justify-between w-full max-w-2xl mx-auto mt-8 pt-4 border-t border-stone-200",
    )


def transaction_wizard() -> rx.Component:
    """The main transaction entry wizard component."""
    return rx.el.div(
        wizard_progress(),
        rx.el.div(
            rx.match(
                TransactionState.current_step,
                (1, step_1_type()),
                (2, step_2_category()),
                (3, step_3_amount()),
                (4, step_4_date()),
                (5, step_5_notes()),
                (6, step_6_review()),
                (7, step_7_coconut()),
                (8, step_8_milk()),
                rx.el.div("Invalid Step"),
            ),
            class_name="bg-white p-5 md:p-8 rounded-2xl shadow-sm border border-stone-100 w-full max-w-2xl mx-auto min-h-[400px]",
        ),
        wizard_nav(),
        on_mount=TransactionState.reset_wizard,
        class_name="w-full",
    )

import reflex as rx

from app.components.common import BTN_PRIMARY, BTN_SECONDARY
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
    """Clickable step indicators — jump back to any completed step."""
    return rx.el.div(
        rx.foreach(
            TransactionState.wizard_steps,
            lambda step, index: rx.el.div(
                rx.el.button(
                    rx.el.div(
                        rx.cond(
                            TransactionState.current_step > index + 1,
                            rx.icon("check", class_name="h-4 w-4 text-white"),
                            rx.el.span(index + 1, class_name="text-xs font-semibold"),
                        ),
                        class_name=rx.cond(
                            TransactionState.current_step > index,
                            "flex items-center justify-center w-7 h-7 rounded-full bg-emerald-500 text-white transition-all duration-300 scale-100 shadow-sm",
                            "flex items-center justify-center w-7 h-7 rounded-full bg-stone-200 text-stone-600 dark:bg-stone-700 dark:text-stone-300 transition-all duration-300 dark:bg-stone-700 dark:text-stone-300",
                        ),
                    ),
                    rx.el.p(
                        step,
                        class_name=rx.cond(
                            TransactionState.current_step > index,
                            "text-xs font-semibold text-emerald-600 mt-1 hidden sm:block transition-colors",
                            "text-xs font-medium text-stone-500 dark:text-stone-400 mt-1 hidden sm:block transition-colors dark:text-stone-400",
                        ),
                    ),
                    on_click=TransactionState.go_to_step(index + 1),
                    disabled=TransactionState.current_step <= index + 1,
                    aria_label=f"Go to step {index + 1}: {step}",
                    class_name="flex flex-col items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/50 rounded-lg disabled:cursor-default min-w-[40px] min-h-[40px] pt-1",
                ),
                rx.cond(
                    index < TransactionState.wizard_steps.length() - 1,
                    rx.el.div(
                        rx.el.div(
                            class_name=rx.cond(
                                TransactionState.current_step > index + 1,
                                "al-grow-x h-0.5 w-full bg-emerald-500 origin-left",
                                "h-0.5 w-full bg-stone-200 dark:bg-stone-700",
                            )
                        ),
                        class_name="flex-1 h-0.5 overflow-hidden",
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
            class_name=f"px-6 py-2.5 min-h-[40px] {BTN_SECONDARY}",
            disabled=TransactionState.current_step == 1,
        ),
        rx.cond(
            TransactionState.current_step >= 6,
            rx.el.button(
                rx.cond(
                    TransactionState.is_submitting,
                    rx.icon("loader-circle", class_name="h-4 w-4 animate-spin mr-2"),
                    None,
                ),
                rx.cond(
                    TransactionState.is_submitting,
                    "Submitting…",
                    "Submit Transaction",
                ),
                on_click=TransactionState.submit_transaction,
                disabled=TransactionState.is_submitting,
                class_name=f"px-6 py-2.5 min-h-[40px] {BTN_PRIMARY} inline-flex items-center",
            ),
            rx.el.button(
                "Next",
                on_click=TransactionState.next_step,
                class_name=f"px-6 py-2.5 min-h-[40px] {BTN_PRIMARY}",
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
        class_name="flex justify-between w-full max-w-2xl mx-auto mt-8 pt-4 border-t border-stone-200 dark:border-stone-700",
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
            class_name="bg-white p-5 md:p-8 rounded-2xl shadow-sm border border-stone-100 w-full max-w-2xl mx-auto min-h-[400px] dark:bg-stone-900 dark:border-stone-700",
        ),
        wizard_nav(),
        on_mount=TransactionState.reset_wizard,
        class_name="w-full",
    )


import reflex as rx

from app.components.common import BTN_PRIMARY, BTN_SECONDARY, modal_shell
from app.states.breeding_state import BreedingState, CalvingRecordDialogState


def timeline_step(
    title: str,
    date: rx.Var[str],
    is_complete: rx.Var[bool],
    is_active: rx.Var[bool],
    icon: str,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name="h-5 w-5"),
                class_name=rx.cond(
                    is_complete,
                    "flex items-center justify-center w-10 h-10 rounded-full bg-emerald-500 text-white transition-all duration-300 shadow-sm",
                    rx.cond(
                        is_active,
                        "flex items-center justify-center w-10 h-10 rounded-full bg-blue-500 text-white ring-4 ring-blue-200 transition-all duration-300 animate-pulse dark:ring-blue-900",
                        "flex items-center justify-center w-10 h-10 rounded-full bg-stone-200 text-stone-500 transition-all duration-300 dark:bg-stone-700 dark:text-stone-400",
                    ),
                ),
            ),
            rx.el.div(
                rx.el.p(
                    title,
                    class_name="font-semibold text-stone-700 dark:text-stone-200",
                ),
                rx.el.p(
                    date,
                    class_name="text-xs text-stone-500 dark:text-stone-400",
                ),
                class_name="mt-2 text-center",
            ),
        ),
        class_name="flex-shrink-0 flex flex-col items-center",
    )


def timeline_connector(is_complete: rx.Var[bool]) -> rx.Component:
    return rx.el.div(
        class_name=rx.cond(
            is_complete,
            "al-grow-x flex-1 h-1 bg-emerald-500 origin-left",
            "flex-1 h-1 bg-stone-200 dark:bg-stone-700",
        )
    )


def breeding_timeline_visual() -> rx.Component:
    cycle = BreedingState.current_breeding_cycle
    is_pregnant = cycle["status"] == "pregnant"
    is_calved = cycle["status"] == "calved"
    is_not_pregnant = cycle["status"] == "not_pregnant"
    pregnancy_check_due_date = BreedingState.pregnancy_check_due_date_str
    return rx.el.div(
        rx.el.h3(
            "Breeding Timeline", class_name="text-lg font-semibold text-stone-800 mb-6 dark:text-stone-100"
        ),
        rx.el.div(
            timeline_step(
                "Hormone", cycle["hormone_injection_date"], True, False, "syringe"
            ),
            timeline_connector(True),
            timeline_step(
                "Insemination", cycle["insemination_date"], True, False, "atom"
            ),
            timeline_connector(is_pregnant | is_calved | is_not_pregnant),
            timeline_step(
                "Pregnancy Check",
                rx.cond(
                    cycle["pregnancy_confirmation_date"],
                    cycle["pregnancy_confirmation_date"],
                    f"Due by {pregnancy_check_due_date}",
                ),
                is_pregnant | is_calved | is_not_pregnant,
                cycle["status"] == "pending_confirmation",
                "clipboard-check",
            ),
            timeline_connector(is_calved),
            timeline_step(
                "Expected Calving",
                cycle["expected_calving_date"],
                is_calved,
                is_pregnant,
                "baby",
            ),
            class_name="flex items-center w-full",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700",
    )


def pregnancy_confirmation_dialog() -> rx.Component:
    return modal_shell(
        rx.el.div(
            rx.el.h2(
                "Confirm Pregnancy",
                class_name="text-xl font-bold text-stone-800 dark:text-stone-100",
            ),
            rx.el.p(
                f"Animal: {BreedingState.current_breeding_cycle['cattle_name']}",
                class_name="text-sm text-stone-500 dark:text-stone-400 mt-1 dark:text-stone-400",
            ),
            rx.el.div(
                rx.el.label(
                    "Outcome", class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300"
                ),
                rx.el.select(
                    rx.el.option("Pregnant", value="pregnant"),
                    rx.el.option("Not Pregnant", value="not_pregnant"),
                    value=BreedingState.pregnancy_confirmation_outcome,
                    on_change=BreedingState.set_pregnancy_confirmation_outcome,
                    class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                rx.el.label(
                    "Confirmation Date",
                    class_name="block text-sm font-medium text-stone-700 mb-1 mt-4 dark:text-stone-300",
                ),
                rx.el.input(
                    type="date",
                    value=BreedingState.pregnancy_confirmation_date,
                    on_change=BreedingState.set_pregnancy_confirmation_date,
                    class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                class_name="my-6",
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    on_click=lambda: BreedingState.set_show_pregnancy_confirmation_dialog(
                        False
                    ),
                    class_name=f"px-4 py-2 {BTN_SECONDARY}",
                ),
                rx.el.button(
                    "Save Result",
                    on_click=lambda: BreedingState.update_pregnancy_status(
                        BreedingState.current_breeding_cycle["id"],
                        BreedingState.pregnancy_confirmation_outcome == "pregnant",
                        BreedingState.pregnancy_confirmation_date,
                    ),
                    class_name=f"px-4 py-2 {BTN_PRIMARY}",
                ),
                class_name="flex justify-end gap-4",
            ),
        ),
        BreedingState.show_pregnancy_confirmation_dialog,
        lambda: BreedingState.set_show_pregnancy_confirmation_dialog(False),
    )


def calving_record_dialog() -> rx.Component:
    return modal_shell(
        rx.el.div(
            rx.el.h2(
                "Record Calving Outcome",
                class_name="text-xl font-bold text-stone-800 dark:text-stone-100",
            ),
            rx.cond(
                BreedingState.calving_error != "",
                rx.el.div(
                    rx.icon(
                        "triangle-alert", class_name="h-4 w-4 mr-2 flex-shrink-0"
                    ),
                    BreedingState.calving_error,
                    class_name="flex items-start text-red-600 text-sm bg-red-50 border border-red-200 p-3 rounded-lg mt-3 dark:bg-red-950/40",
                ),
                None,
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.label("Birth Outcome", class_name="text-sm font-medium dark:text-stone-200"),
                    rx.el.select(
                        rx.foreach(
                            CalvingRecordDialogState.outcome_options,
                            lambda o: rx.el.option(o[1], value=o[0]),
                        ),
                        name="birth_outcome",
                        class_name="mt-1 w-full p-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        on_change=CalvingRecordDialogState.set_birth_outcome,
                    ),
                    rx.cond(
                        CalvingRecordDialogState.birth_outcome == "live_birth",
                        rx.el.div(
                            rx.el.label(
                                "Calf Sex", class_name="text-sm font-medium dark:text-stone-200"
                            ),
                            rx.el.select(
                                rx.el.option("Male", value="male"),
                                rx.el.option("Female", value="female"),
                                name="calf_sex",
                                class_name="mt-1 w-full p-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                            ),
                            rx.el.label(
                                "Calf Health", class_name="text-sm font-medium dark:text-stone-200"
                            ),
                            rx.el.input(
                                name="calf_health",
                                placeholder="e.g., Healthy and active",
                                class_name="mt-1 w-full p-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                            ),
                            class_name="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4",
                        ),
                        None,
                    ),
                    rx.el.label("Notes", class_name="text-sm font-medium mt-4 dark:text-stone-200"),
                    rx.el.textarea(
                        name="notes",
                        placeholder="Describe the birth process and any observations...",
                        class_name="mt-1 w-full p-2 border rounded-md h-24 dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100",
                    ),
                    class_name="space-y-2 my-6",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=lambda: BreedingState.toggle_calving_record_dialog(
                            False
                        ),
                        class_name=f"px-4 py-2 {BTN_SECONDARY}",
                    ),
                    rx.el.button(
                        "Save Record",
                        type="submit",
                        class_name=f"px-4 py-2 {BTN_PRIMARY}",
                    ),
                    class_name="flex justify-end gap-4",
                ),
                on_submit=lambda form_data: BreedingState.record_calving(
                    BreedingState.current_breeding_cycle["id"], form_data
                ),
            ),
        ),
        BreedingState.show_calving_record_dialog,
        lambda: BreedingState.toggle_calving_record_dialog(False),
    )


def detail_card_action_button(
    icon: str, label: str, on_click: rx.event.EventHandler, color_class: str
) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-4 w-4 mr-2"),
        label,
        on_click=on_click,
        class_name=f"flex items-center text-sm font-semibold px-4 py-2 rounded-lg transition-all {color_class}",
    )


def actions_section() -> rx.Component:
    cycle = BreedingState.current_breeding_cycle
    return rx.el.div(
        rx.el.h3("Actions", class_name="text-lg font-semibold text-stone-800 dark:text-stone-100"),
        rx.el.div(
            rx.cond(
                cycle["status"] == "pending_confirmation",
                detail_card_action_button(
                    "clipboard-check",
                    "Confirm Pregnancy",
                    lambda: BreedingState.set_show_pregnancy_confirmation_dialog(True),
                    "bg-blue-500 text-white hover:bg-blue-600",
                ),
                None,
            ),
            rx.cond(
                cycle["status"] == "pregnant",
                detail_card_action_button(
                    "baby",
                    "Record Calving",
                    lambda: BreedingState.toggle_calving_record_dialog(True),
                    "bg-emerald-500 text-white hover:bg-emerald-600",
                ),
                None,
            ),
            detail_card_action_button(
                "plus",
                "Add Follow-up Note",
                lambda: BreedingState.toggle_follow_up_dialog(True),
                "bg-stone-200 text-stone-800 hover:bg-stone-300 dark:bg-stone-700 dark:text-stone-100 dark:hover:bg-stone-600",
            ),
            class_name="mt-4 flex gap-4",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border mt-6 dark:bg-stone-900 dark:border-stone-700",
    )


def follow_up_checks_list() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Follow-up Checks", class_name="text-lg font-semibold text-stone-800 dark:text-stone-100"),
        rx.el.div(
            rx.foreach(
                BreedingState.current_breeding_cycle["follow_up_checks"],
                lambda check: rx.el.div(
                    rx.el.p(check["date"], class_name="font-semibold text-sm"),
                    rx.el.p(check["notes"], class_name="text-sm"),
                    class_name="py-2 border-b",
                ),
            ),
            class_name="mt-4 space-y-2",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border dark:bg-stone-900 dark:border-stone-700",
    )


def follow_up_dialog() -> rx.Component:
    """Dialog to record a follow-up check on the current breeding cycle."""
    return modal_shell(
        rx.el.div(
            rx.el.h2(
                "Add Follow-up Check",
                class_name="text-xl font-bold text-stone-800 dark:text-stone-100",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.label(
                        "Date", class_name="text-sm font-medium dark:text-stone-200"
                    ),
                    rx.el.input(
                        type="date",
                        default_value=BreedingState.follow_up_date,
                        on_change=BreedingState.set_follow_up_date,
                        class_name="mt-1 w-full p-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                    ),
                    rx.el.label(
                        "Notes", class_name="text-sm font-medium mt-4 dark:text-stone-200"
                    ),
                    rx.el.textarea(
                        placeholder="e.g., Ultrasound check normal...",
                        value=BreedingState.follow_up_notes,
                        on_change=BreedingState.set_follow_up_notes,
                        class_name="mt-1 w-full p-2 border rounded-md h-24 dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100",
                    ),
                    class_name="space-y-2 my-6",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=lambda: BreedingState.toggle_follow_up_dialog(
                            False
                        ),
                        class_name=f"px-4 py-2 {BTN_SECONDARY}",
                    ),
                    rx.el.button(
                        "Save Check",
                        type="submit",
                        class_name=f"px-4 py-2 {BTN_PRIMARY}",
                    ),
                    class_name="flex justify-end gap-4",
                ),
                on_submit=lambda _form_data: BreedingState.submit_follow_up_check(),
            ),
        ),
        BreedingState.show_follow_up_dialog,
        lambda: BreedingState.toggle_follow_up_dialog(False),
    )


def breeding_detail_content() -> rx.Component:
    return rx.el.div(
        breeding_timeline_visual(),
        actions_section(),
        rx.el.div(follow_up_checks_list(), class_name="mt-6"),
        pregnancy_confirmation_dialog(),
        calving_record_dialog(),
        follow_up_dialog(),
    )


def breeding_detail_page() -> rx.Component:
    """The detail page for a single breeding cycle."""
    return rx.cond(
        BreedingState.current_breeding_cycle,
        breeding_detail_content(),
        rx.el.p("Loading breeding cycle details..."),
    )

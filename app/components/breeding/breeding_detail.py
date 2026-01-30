import reflex as rx
from app.states.breeding_state import BreedingState, CalvingRecordDialogState
import datetime


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
                    "flex items-center justify-center w-10 h-10 rounded-full bg-emerald-500 text-white",
                    rx.cond(
                        is_active,
                        "flex items-center justify-center w-10 h-10 rounded-full bg-blue-500 text-white ring-4 ring-blue-200",
                        "flex items-center justify-center w-10 h-10 rounded-full bg-stone-200 text-stone-500",
                    ),
                ),
            ),
            rx.el.div(
                rx.el.p(title, class_name="font-semibold text-stone-700"),
                rx.el.p(date, class_name="text-xs text-stone-500"),
                class_name="mt-2 text-center",
            ),
        ),
        class_name="flex-shrink-0 flex flex-col items-center",
    )


def timeline_connector(is_complete: rx.Var[bool]) -> rx.Component:
    return rx.el.div(
        class_name=rx.cond(
            is_complete, "flex-1 h-1 bg-emerald-500", "flex-1 h-1 bg-stone-200"
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
            "Breeding Timeline", class_name="text-lg font-semibold text-stone-800 mb-6"
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
        class_name="bg-white p-6 rounded-2xl shadow-sm border",
    )


def pregnancy_confirmation_dialog() -> rx.Component:
    return rx.cond(
        BreedingState.show_pregnancy_confirmation_dialog,
        rx.el.div(
            rx.el.div(
                class_name="fixed inset-0 bg-black/50 z-40",
                on_click=lambda: BreedingState.set_show_pregnancy_confirmation_dialog(
                    False
                ),
            ),
            rx.el.div(
                class_name="bg-white p-8 rounded-2xl shadow-xl w-full max-w-lg z-50"
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def calving_record_dialog() -> rx.Component:
    return rx.cond(
        BreedingState.show_calving_record_dialog,
        rx.el.div(
            rx.el.div(
                class_name="fixed inset-0 bg-black/50 z-40",
                on_click=lambda: BreedingState.toggle_calving_record_dialog(False),
            ),
            rx.el.div(
                rx.el.h2(
                    "Record Calving Outcome",
                    class_name="text-xl font-bold text-stone-800",
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label("Birth Outcome", class_name="text-sm font-medium"),
                        rx.el.select(
                            rx.foreach(
                                CalvingRecordDialogState.outcome_options,
                                lambda o: rx.el.option(o[1], value=o[0]),
                            ),
                            name="birth_outcome",
                            class_name="mt-1 w-full p-2 border rounded-md",
                            on_change=CalvingRecordDialogState.set_birth_outcome,
                        ),
                        rx.cond(
                            CalvingRecordDialogState.birth_outcome == "live_birth",
                            rx.el.div(
                                rx.el.label(
                                    "Calf Sex", class_name="text-sm font-medium"
                                ),
                                rx.el.select(
                                    rx.el.option("Male", value="male"),
                                    rx.el.option("Female", value="female"),
                                    name="calf_sex",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                rx.el.label(
                                    "Calf Health", class_name="text-sm font-medium"
                                ),
                                rx.el.input(
                                    name="calf_health",
                                    placeholder="e.g., Healthy and active",
                                    class_name="mt-1 w-full p-2 border rounded-md",
                                ),
                                class_name="grid grid-cols-2 gap-4 mt-4",
                            ),
                            None,
                        ),
                        rx.el.label("Notes", class_name="text-sm font-medium mt-4"),
                        rx.el.textarea(
                            name="notes",
                            placeholder="Describe the birth process and any observations...",
                            class_name="mt-1 w-full p-2 border rounded-md h-24",
                        ),
                        class_name="space-y-2 my-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=lambda: BreedingState.toggle_calving_record_dialog(
                                False
                            ),
                            class_name="px-4 py-2 bg-stone-200 rounded-md font-semibold",
                        ),
                        rx.el.button(
                            "Save Record",
                            type="submit",
                            class_name="px-4 py-2 bg-emerald-500 text-white rounded-md font-semibold",
                        ),
                        class_name="flex justify-end gap-4",
                    ),
                    on_submit=lambda form_data: BreedingState.record_calving(
                        BreedingState.current_breeding_cycle["id"], form_data
                    ),
                    reset_on_submit=True,
                ),
                class_name="bg-white p-8 rounded-2xl shadow-xl w-full max-w-lg z-50",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
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
        rx.el.h3("Actions", class_name="text-lg font-semibold text-stone-800"),
        rx.el.div(
            rx.cond(
                cycle["status"] == "pending_confirmation",
                detail_card_action_button(
                    "clipboard-check",
                    "Confirm Pregnancy",
                    rx.toast.info("Pregnancy confirmation not implemented yet."),
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
                rx.toast.info("Follow-up notes not implemented yet."),
                "bg-stone-200 text-stone-800 hover:bg-stone-300",
            ),
            class_name="mt-4 flex gap-4",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border mt-6",
    )


def follow_up_checks_list() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Follow-up Checks", class_name="text-lg font-semibold text-stone-800"),
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
        class_name="bg-white p-6 rounded-2xl shadow-sm border",
    )


def breeding_detail_content() -> rx.Component:
    return rx.el.div(
        breeding_timeline_visual(),
        actions_section(),
        rx.el.div(follow_up_checks_list(), class_name="mt-6"),
        pregnancy_confirmation_dialog(),
        calving_record_dialog(),
    )


def breeding_detail_page() -> rx.Component:
    """The detail page for a single breeding cycle."""
    return rx.cond(
        BreedingState.current_breeding_cycle,
        breeding_detail_content(),
        rx.el.p("Loading breeding cycle details..."),
    )
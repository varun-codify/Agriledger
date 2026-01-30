import reflex as rx
from app.states.breeding_state import BreedingState
from app.states.cattle_state import CattleState


def breeding_cycle_card(cycle: rx.Var[dict]) -> rx.Component:
    status = cycle["status"]
    status_color = rx.match(
        status,
        ("pending_confirmation", "bg-yellow-100 text-yellow-800"),
        ("pregnant", "bg-emerald-100 text-emerald-800"),
        ("calved", "bg-blue-100 text-blue-800"),
        ("not_pregnant", "bg-red-100 text-red-800"),
        "bg-stone-100 text-stone-800",
    )
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    cycle["cattle_name"], class_name="font-bold text-lg text-stone-800"
                ),
                rx.el.p(
                    f"Inseminated: {cycle['insemination_date']}",
                    class_name="text-xs text-stone-500",
                ),
                class_name="flex-1",
            ),
            rx.el.span(
                status.replace("_", " ").capitalize(),
                class_name=f"px-2 py-1 text-xs font-semibold rounded-full {status_color}",
            ),
            class_name="flex items-start justify-between",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("calendar-check-2", class_name="h-4 w-4 text-stone-500"),
                rx.el.p(
                    "Pregnancy Check:", class_name="text-sm font-medium text-stone-600"
                ),
                rx.el.p(
                    cycle["pregnancy_confirmation_date"] | "Pending",
                    class_name="text-sm font-semibold",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.div(
                rx.icon("baby", class_name="h-4 w-4 text-stone-500"),
                rx.el.p(
                    "Est. Calving:", class_name="text-sm font-medium text-stone-600"
                ),
                rx.el.p(
                    cycle["expected_calving_date"], class_name="text-sm font-semibold"
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="mt-4 flex justify-between text-sm",
        ),
        href=f"/cattle/breeding/{cycle['id']}",
        class_name="bg-white p-4 rounded-2xl shadow-sm border border-stone-100 hover:shadow-lg hover:-translate-y-1 transition-all",
    )


def filter_button(label: str, filter_value: str) -> rx.Component:
    is_selected = BreedingState.selected_filter == filter_value
    return rx.el.button(
        label,
        on_click=lambda: BreedingState.set_filter(filter_value),
        class_name=rx.cond(
            is_selected,
            "px-4 py-1.5 rounded-lg text-sm font-semibold bg-emerald-500 text-white shadow-sm",
            "px-4 py-1.5 rounded-lg text-sm font-semibold bg-white text-stone-600 border hover:bg-stone-50",
        ),
    )


def filter_tabs() -> rx.Component:
    return rx.el.div(
        filter_button("All", "all"),
        filter_button("Pending Confirmation", "pending_confirmation"),
        filter_button("Pregnant", "pregnant"),
        filter_button("Calved", "calved"),
        filter_button("Not Pregnant", "not_pregnant"),
        class_name="flex gap-2",
    )


def alert_item(icon: str, title: str, items: rx.Var[list], color: str) -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            rx.icon(icon, class_name=f"h-5 w-5 mr-2 text-{color}-600"),
            title,
            class_name=f"flex items-center font-semibold text-{color}-800",
        ),
        rx.el.ul(
            rx.foreach(
                items,
                lambda item: rx.el.li(
                    f"{item['cattle_name']} (Inseminated: {item['insemination_date']})",
                    class_name="text-sm",
                ),
            ),
            class_name="list-disc list-inside mt-2 space-y-1 text-stone-700",
        ),
        class_name=f"bg-{color}-50 border-l-4 border-{color}-500 p-4 rounded-r-lg",
    )


def breeding_alerts_section() -> rx.Component:
    return rx.el.div(
        rx.cond(
            BreedingState.pregnancy_checks_due.length() > 0,
            alert_item(
                "clipboard-check",
                "Pregnancy Checks Due",
                BreedingState.pregnancy_checks_due,
                "yellow",
            ),
            None,
        ),
        rx.cond(
            BreedingState.calvings_due_soon.length() > 0,
            alert_item(
                "siren", "Calvings Due Soon", BreedingState.calvings_due_soon, "red"
            ),
            None,
        ),
        class_name="grid md:grid-cols-2 gap-6 mb-6",
    )


def add_breeding_dialog() -> rx.Component:
    return rx.cond(
        BreedingState.show_add_breeding_dialog,
        rx.el.div(
            rx.el.div(
                on_click=lambda: BreedingState.toggle_add_breeding_dialog(False),
                class_name="fixed inset-0 bg-black/50 z-40",
            ),
            rx.el.div(
                rx.el.h2(
                    "Start New Breeding Cycle",
                    class_name="text-2xl font-bold text-stone-800",
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label(
                            "Select Animal (Cow/Buffalo)",
                            class_name="text-sm font-medium",
                        ),
                        rx.el.select(
                            rx.foreach(
                                CattleState.breedable_females,
                                lambda c: rx.el.option(c["name"], value=c["id"]),
                            ),
                            name="cattle_id",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Hormone Injection Date", class_name="text-sm font-medium"
                        ),
                        rx.el.input(
                            name="hormone_injection_date",
                            type="date",
                            default_value=BreedingState.new_hormone_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Insemination Date", class_name="text-sm font-medium"
                        ),
                        rx.el.input(
                            name="insemination_date",
                            type="date",
                            default_value=BreedingState.new_insemination_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Notes (optional)", class_name="text-sm font-medium"
                        ),
                        rx.el.textarea(
                            name="notes", class_name="mt-1 w-full p-2 border rounded-md"
                        ),
                        class_name="space-y-4 my-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            type="button",
                            on_click=lambda: BreedingState.toggle_add_breeding_dialog(
                                False
                            ),
                            class_name="w-full py-2 rounded-lg bg-stone-200 text-stone-800 font-semibold",
                        ),
                        rx.el.button(
                            "Start Cycle",
                            type="submit",
                            class_name="w-full py-2 rounded-lg bg-emerald-500 text-white font-semibold",
                        ),
                        class_name="flex gap-4 mt-6",
                    ),
                    on_submit=BreedingState.add_breeding_cycle,
                    reset_on_submit=True,
                ),
                class_name="bg-white p-8 rounded-2xl shadow-xl w-full max-w-lg z-50",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def breeding_list_page() -> rx.Component:
    """The main page for managing breeding cycles."""
    return rx.el.div(
        breeding_alerts_section(),
        rx.el.div(
            filter_tabs(),
            rx.el.button(
                rx.icon("plus", class_name="h-4 w-4 mr-2"),
                "New Breeding Cycle",
                on_click=lambda: BreedingState.toggle_add_breeding_dialog(True),
                class_name="flex items-center bg-emerald-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-emerald-600 transition-all",
            ),
            class_name="flex items-center justify-between mb-6",
        ),
        rx.el.div(
            rx.foreach(BreedingState.filtered_breeding_cycles, breeding_cycle_card),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
        ),
        add_breeding_dialog(),
    )
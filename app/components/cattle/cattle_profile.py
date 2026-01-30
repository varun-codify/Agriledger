import reflex as rx
from app.states.cattle_state import (
    CattleState,
    MilkProduction,
    VaccinationRecord,
    HealthNote,
)
from app.components.layout import dashboard_layout


def health_status_badge(status: rx.Var[str]) -> rx.Component:
    return rx.el.span(
        status,
        class_name=rx.match(
            status,
            (
                "Healthy",
                "px-3 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800",
            ),
            (
                "Vaccinated",
                "px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800",
            ),
            (
                "Sick",
                "px-3 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800",
            ),
            (
                "Under Treatment",
                "px-3 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800",
            ),
            "px-3 py-1 text-xs font-semibold rounded-full bg-stone-100 text-stone-600",
        ),
    )


def metric_card(icon: str, label: str, value: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-6 w-6 text-stone-500"),
        rx.el.div(
            rx.el.p(label, class_name="text-sm text-stone-500"),
            rx.el.p(value, class_name="text-lg font-bold text-stone-800"),
            class_name="ml-3",
        ),
        class_name="flex items-center bg-white p-4 rounded-xl shadow-sm border border-stone-100",
    )


def profile_action_button(
    icon: str, label: str, on_click: rx.event.EventHandler
) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-4 w-4 mr-2"),
        label,
        on_click=on_click,
        class_name="flex items-center bg-white text-stone-700 px-4 py-2 rounded-lg font-semibold border border-stone-200 hover:bg-stone-50 transition-all text-sm",
    )


def profile_tabs() -> rx.Component:
    tabs = ["Overview", "Milk History", "Health Records", "Feed Records"]
    return rx.el.div(
        rx.foreach(
            tabs,
            lambda tab: rx.el.button(
                tab,
                on_click=lambda: CattleState.set_profile_tab(tab),
                class_name=rx.cond(
                    CattleState.profile_active_tab == tab,
                    "px-4 py-2 font-semibold text-emerald-600 border-b-2 border-emerald-500",
                    "px-4 py-2 font-medium text-stone-500 hover:text-stone-800",
                ),
            ),
        ),
        class_name="flex border-b border-stone-200",
    )


def milk_production_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Milk Production (Last 30 Days)",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(
                vertical=False, stroke_dasharray="3 3", class_name="stroke-stone-200"
            ),
            rx.recharts.graphing_tooltip(cursor={"fill": "rgba(231, 229, 228, 0.4)"}),
            rx.recharts.x_axis(
                data_key="date",
                tick_line=False,
                axis_line=False,
                class_name="text-xs text-stone-500",
            ),
            rx.recharts.y_axis(
                tick_line=False,
                axis_line=False,
                class_name="text-xs text-stone-500",
                domain=["dataMin - 1", "dataMax + 1"],
            ),
            rx.recharts.line(
                data_key="liters",
                stroke="#10b981",
                stroke_width=2,
                dot=False,
                type_="monotone",
            ),
            data=CattleState.milk_production_last_30_days,
            height=300,
            class_name="w-full",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-2",
    )


def timeline_item(
    date: rx.Var, title: rx.Var, description: rx.Var, icon: str, color_class: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-5 w-5 text-white"),
            class_name=f"absolute -left-4 top-0.5 flex items-center justify-center w-8 h-8 rounded-full {color_class}",
        ),
        rx.el.div(
            rx.el.time(date, class_name="text-xs font-medium text-stone-500"),
            rx.el.h3(title, class_name="font-semibold text-stone-800"),
            rx.el.p(description, class_name="text-sm text-stone-600"),
            class_name="ml-8",
        ),
        class_name="relative pl-4 border-l-2 border-stone-200",
    )


def health_timeline() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Health & Vaccination Timeline",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.el.div(
            rx.foreach(
                CattleState.current_cattle["vaccinations"],
                lambda v: timeline_item(
                    v["date"],
                    f"Vaccination: {v['vaccine_name']}",
                    f"Administered by {v['veterinarian']}. Notes: {v.get('notes', 'N/A')}",
                    "syringe",
                    "bg-blue-500",
                ),
            ),
            rx.foreach(
                CattleState.current_cattle["health_notes"],
                lambda n: timeline_item(
                    n["date"],
                    f"Health Note: {n['severity']}",
                    n["note"],
                    "heart-pulse",
                    rx.match(
                        n["severity"],
                        ("Critical", "bg-red-500"),
                        ("Attention Needed", "bg-yellow-500"),
                        ("Normal", "bg-emerald-500"),
                        "bg-stone-500",
                    ),
                ),
            ),
            class_name="space-y-6",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def overview_tab_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            metric_card(
                "cake", "Age", CattleState.current_cattle["age"].to_string() + " years"
            ),
            metric_card(
                "dollar-sign",
                "Purchase Price",
                "$" + CattleState.current_cattle["purchase_price"].to_string(),
            ),
            metric_card(
                "calendar-days",
                "Purchase Date",
                CattleState.current_cattle["purchase_date"],
            ),
            metric_card("hourglass", "Days Owned", CattleState.days_owned.to_string()),
            metric_card(
                "droplets",
                "Total Milk",
                CattleState.total_milk_produced.to_string() + " L",
            ),
            metric_card(
                "activity",
                "Avg. Daily Milk",
                CattleState.average_daily_milk.to_string() + " L",
            ),
            class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6",
        ),
        rx.el.div(
            milk_production_chart(),
            health_timeline(),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6",
        ),
    )


def milk_history_tab_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Date", class_name="px-4 py-2 text-left"),
                        rx.el.th("Liters", class_name="px-4 py-2 text-left"),
                        rx.el.th("Notes", class_name="px-4 py-2 text-left"),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        CattleState.current_cattle["milk_production"],
                        lambda record: rx.el.tr(
                            rx.el.td(record["date"], class_name="px-4 py-2 border-t"),
                            rx.el.td(record["liters"], class_name="px-4 py-2 border-t"),
                            rx.el.td(
                                record["notes"] | "-", class_name="px-4 py-2 border-t"
                            ),
                        ),
                    )
                ),
                class_name="w-full text-sm",
            ),
            class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
        )
    )


def add_milk_dialog() -> rx.Component:
    return rx.cond(
        CattleState.show_milk_dialog,
        rx.el.div(
            rx.el.div(
                on_click=lambda: CattleState.toggle_milk_dialog(False),
                class_name="fixed inset-0 bg-black/50 z-40",
            ),
            rx.el.div(
                rx.el.h2(
                    "Add Milk Entry", class_name="text-xl font-bold text-stone-800"
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label("Date", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="date",
                            type="date",
                            default_value=CattleState.current_dialog_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Liters", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="liters",
                            type="number",
                            step="0.1",
                            placeholder="e.g., 12.5",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Notes (Optional)", class_name="text-sm font-medium"
                        ),
                        rx.el.textarea(
                            name="notes",
                            placeholder="Any observations...",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        class_name="space-y-4 my-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=lambda: CattleState.toggle_milk_dialog(False),
                            class_name="px-4 py-2 bg-stone-200 rounded-md font-semibold",
                        ),
                        rx.el.button(
                            "Save Entry",
                            type="submit",
                            class_name="px-4 py-2 bg-emerald-500 text-white rounded-md font-semibold",
                        ),
                        class_name="flex justify-end gap-4",
                    ),
                    on_submit=CattleState.add_milk_entry,
                    reset_on_submit=True,
                ),
                class_name="bg-white p-8 rounded-2xl shadow-xl w-full max-w-lg z-50",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def add_vaccination_dialog() -> rx.Component:
    return rx.cond(
        CattleState.show_vaccination_dialog,
        rx.el.div(
            rx.el.div(
                on_click=lambda: CattleState.toggle_vaccination_dialog(False),
                class_name="fixed inset-0 bg-black/50 z-40",
            ),
            rx.el.div(
                rx.el.h2(
                    "Record Vaccination", class_name="text-xl font-bold text-stone-800"
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label("Vaccine Name", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="vaccine_name",
                            placeholder="e.g., FMD Vaccine",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Date Administered", class_name="text-sm font-medium"
                        ),
                        rx.el.input(
                            name="date",
                            type="date",
                            default_value=CattleState.current_dialog_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Veterinarian", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="veterinarian",
                            placeholder="e.g., Dr. Smith",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Next Due Date (Optional)", class_name="text-sm font-medium"
                        ),
                        rx.el.input(
                            name="next_due_date",
                            type="date",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Notes (Optional)", class_name="text-sm font-medium"
                        ),
                        rx.el.textarea(
                            name="notes", class_name="mt-1 w-full p-2 border rounded-md"
                        ),
                        class_name="grid grid-cols-2 gap-4 my-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=lambda: CattleState.toggle_vaccination_dialog(
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
                    on_submit=CattleState.add_vaccination_record,
                    reset_on_submit=True,
                ),
                class_name="bg-white p-8 rounded-2xl shadow-xl w-full max-w-2xl z-50",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def add_health_note_dialog() -> rx.Component:
    return rx.cond(
        CattleState.show_health_note_dialog,
        rx.el.div(
            rx.el.div(
                on_click=lambda: CattleState.toggle_health_note_dialog(False),
                class_name="fixed inset-0 bg-black/50 z-40",
            ),
            rx.el.div(
                rx.el.h2(
                    "Add Health Note", class_name="text-xl font-bold text-stone-800"
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label("Date", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="date",
                            type="date",
                            default_value=CattleState.current_dialog_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Severity", class_name="text-sm font-medium"),
                        rx.el.select(
                            rx.el.option("Normal", value="Normal"),
                            rx.el.option("Attention Needed", value="Attention Needed"),
                            rx.el.option("Critical", value="Critical"),
                            name="severity",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Note", class_name="text-sm font-medium col-span-2"
                        ),
                        rx.el.textarea(
                            name="note",
                            placeholder="Observations about health or behavior...",
                            class_name="mt-1 w-full p-2 border rounded-md col-span-2 h-24",
                        ),
                        class_name="grid grid-cols-2 gap-4 my-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=lambda: CattleState.toggle_health_note_dialog(
                                False
                            ),
                            class_name="px-4 py-2 bg-stone-200 rounded-md font-semibold",
                        ),
                        rx.el.button(
                            "Save Note",
                            type="submit",
                            class_name="px-4 py-2 bg-emerald-500 text-white rounded-md font-semibold",
                        ),
                        class_name="flex justify-end gap-4",
                    ),
                    on_submit=CattleState.add_health_note,
                    reset_on_submit=True,
                ),
                class_name="bg-white p-8 rounded-2xl shadow-xl w-full max-w-2xl z-50",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def cattle_profile_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.image(
                    src=CattleState.current_cattle["image_url"],
                    class_name="h-32 w-32 rounded-full shadow-lg border-4 border-white object-cover",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            CattleState.current_cattle["name"],
                            class_name="text-3xl font-bold text-stone-800",
                        ),
                        rx.el.span(
                            f"#{CattleState.current_cattle['tag_number']}",
                            class_name="text-sm font-mono px-2 py-1 bg-stone-100 text-stone-600 rounded-md",
                        ),
                        health_status_badge(
                            CattleState.current_cattle["health_status"]
                        ),
                        class_name="flex items-center gap-3",
                    ),
                    rx.el.p(
                        f"{CattleState.current_cattle['breed']} {CattleState.current_cattle['animal_type']}",
                        class_name="text-stone-600",
                    ),
                    class_name="mt-4",
                ),
                class_name="flex items-center space-x-6",
            ),
            rx.el.div(
                profile_action_button(
                    "plus",
                    "Add Milk Entry",
                    lambda: CattleState.toggle_milk_dialog(True),
                ),
                profile_action_button(
                    "syringe",
                    "Record Vaccination",
                    lambda: CattleState.toggle_vaccination_dialog(True),
                ),
                profile_action_button(
                    "heart-pulse",
                    "Add Health Note",
                    lambda: CattleState.toggle_health_note_dialog(True),
                ),
                profile_action_button(
                    "pencil", "Edit Details", rx.toast.info("Edit not yet implemented.")
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-center justify-between mb-6",
        ),
        profile_tabs(),
        rx.el.div(
            rx.match(
                CattleState.profile_active_tab,
                ("Overview", overview_tab_content()),
                ("Milk History", milk_history_tab_content()),
                ("Health Records", health_timeline()),
                ("Feed Records", rx.el.p("Feed records will be shown here.")),
                rx.el.p("Select a tab"),
            ),
            class_name="mt-6",
        ),
        add_milk_dialog(),
        add_vaccination_dialog(),
        add_health_note_dialog(),
    )


def cattle_profile_page() -> rx.Component:
    return dashboard_layout(
        rx.cond(
            CattleState.profile_loading,
            rx.el.div(
                rx.el.div(
                    class_name="h-32 w-32 rounded-full bg-stone-200 animate-pulse"
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="h-8 w-48 bg-stone-200 rounded-md animate-pulse"
                    ),
                    rx.el.div(
                        class_name="h-6 w-32 bg-stone-200 rounded-md animate-pulse mt-2"
                    ),
                    class_name="ml-6",
                ),
                class_name="flex items-center",
            ),
            rx.cond(
                CattleState.current_cattle,
                cattle_profile_content(),
                rx.el.div(
                    rx.el.h2(
                        "Cattle not found",
                        class_name="text-2xl font-bold text-stone-800",
                    ),
                    rx.el.p(
                        "Could not find cattle data for the given ID.",
                        class_name="text-stone-600",
                    ),
                    class_name="text-center py-20",
                ),
            ),
        ),
        "Cattle Profile",
    )
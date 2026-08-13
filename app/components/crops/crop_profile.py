import reflex as rx

from app.components.layout import dashboard_layout
from app.states.crop_state import CropState


def status_badge(status: rx.Var[str]) -> rx.Component:
    return rx.el.span(
        status,
        class_name=rx.match(
            status,
            (
                "Growing",
                "px-3 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800",
            ),
            (
                "Harvested",
                "px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800",
            ),
            (
                "Planted",
                "px-3 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800",
            ),
            (
                "Fallow",
                "px-3 py-1 text-xs font-semibold rounded-full bg-stone-100 text-stone-600",
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


def action_button(
    icon: str, label: str, on_click: rx.event.EventHandler
) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-4 w-4 mr-2"),
        label,
        on_click=on_click,
        class_name="flex items-center bg-white text-stone-700 px-4 py-2 rounded-lg font-semibold border border-stone-200 hover:bg-stone-50 transition-all text-sm",
    )


def profile_tabs() -> rx.Component:
    tabs = ["Overview", "Activity History", "Harvest Records"]
    return rx.el.div(
        rx.foreach(
            tabs,
            lambda tab: rx.el.button(
                tab,
                on_click=lambda: CropState.set_profile_tab(tab),
                class_name=rx.cond(
                    CropState.profile_active_tab == tab,
                    "px-4 py-2 font-semibold text-emerald-600 border-b-2 border-emerald-500",
                    "px-4 py-2 font-medium text-stone-500 hover:text-stone-800",
                ),
            ),
        ),
        class_name="flex border-b border-stone-200",
    )


def add_activity_dialog() -> rx.Component:
    return rx.cond(
        CropState.show_add_activity_dialog,
        rx.el.div(
            rx.el.div(
                on_click=lambda: CropState.toggle_add_activity_dialog(False),
                class_name="fixed inset-0 bg-black/50 z-40",
            ),
            rx.el.div(
                rx.el.h2(
                    "Add Crop Activity", class_name="text-xl font-bold text-stone-800"
                ),
                rx.cond(
                    CropState.dialog_error != "",
                    rx.el.div(
                        rx.icon(
                            "triangle-alert", class_name="h-4 w-4 mr-2 flex-shrink-0"
                        ),
                        CropState.dialog_error,
                        class_name="flex items-start text-red-600 text-sm bg-red-50 border border-red-200 p-3 rounded-lg mt-3",
                    ),
                    None,
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label("Date", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="date",
                            type="date",
                            default_value=CropState.current_dialog_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Activity Type", class_name="text-sm font-medium"),
                        rx.el.select(
                            rx.foreach(
                                CropState.activity_types,
                                lambda type: rx.el.option(type, value=type),
                            ),
                            name="activity_type",
                            class_name="mt-1 w-full p-2 border rounded-md bg-white",
                        ),
                        rx.el.label("Cost", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="cost",
                            type="number",
                            step="0.01",
                            placeholder="e.g., 150.00",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Notes (Optional)",
                            class_name="text-sm font-medium col-span-2",
                        ),
                        rx.el.textarea(
                            name="notes",
                            class_name="mt-1 w-full p-2 border rounded-md col-span-2 h-20",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-4 my-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            type="button",
                            on_click=lambda: CropState.toggle_add_activity_dialog(
                                False
                            ),
                            class_name="px-4 py-2 bg-stone-200 rounded-md font-semibold",
                        ),
                        rx.el.button(
                            "Save Activity",
                            type="submit",
                            class_name="px-4 py-2 bg-emerald-500 text-white rounded-md font-semibold",
                        ),
                        class_name="flex justify-end gap-4",
                    ),
                    on_submit=CropState.add_activity,
                ),
                class_name="bg-white p-8 rounded-2xl shadow-xl w-full max-w-2xl z-50 max-h-[90vh] overflow-y-auto",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def add_harvest_dialog() -> rx.Component:
    return rx.cond(
        CropState.show_add_harvest_dialog,
        rx.el.div(
            rx.el.div(
                on_click=lambda: CropState.toggle_add_harvest_dialog(False),
                class_name="fixed inset-0 bg-black/50 z-40",
            ),
            rx.el.div(
                rx.el.h2(
                    "Record Harvest", class_name="text-xl font-bold text-stone-800"
                ),
                rx.cond(
                    CropState.dialog_error != "",
                    rx.el.div(
                        rx.icon(
                            "triangle-alert", class_name="h-4 w-4 mr-2 flex-shrink-0"
                        ),
                        CropState.dialog_error,
                        class_name="flex items-start text-red-600 text-sm bg-red-50 border border-red-200 p-3 rounded-lg mt-3",
                    ),
                    None,
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label("Date", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="date",
                            type="date",
                            default_value=CropState.current_dialog_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Quantity", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="quantity",
                            type="number",
                            step="0.01",
                            placeholder="e.g., 1000",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Unit", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="unit",
                            placeholder="e.g., kg, bushels, tons",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Income", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="income",
                            type="number",
                            step="0.01",
                            placeholder="e.g., 7000.00",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-4 my-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            type="button",
                            on_click=lambda: CropState.toggle_add_harvest_dialog(False),
                            class_name="px-4 py-2 bg-stone-200 rounded-md font-semibold",
                        ),
                        rx.el.button(
                            "Save Harvest",
                            type="submit",
                            class_name="px-4 py-2 bg-emerald-500 text-white rounded-md font-semibold",
                        ),
                        class_name="flex justify-end gap-4",
                    ),
                    on_submit=CropState.add_harvest,
                ),
                class_name="bg-white p-8 rounded-2xl shadow-xl w-full max-w-2xl z-50 max-h-[90vh] overflow-y-auto",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def overview_tab_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            metric_card(
                "calendar-clock",
                "Days Since Planting",
                CropState.days_since_planting.to_string(),
            ),
            metric_card(
                "list-checks",
                "Total Activities",
                CropState.current_crop["activities"].length(),
            ),
            metric_card(
                "receipt", "Total Expenses", f"₹{CropState.total_expenses.to_string()}"
            ),
            metric_card(
                "banknote",
                "Harvest Income",
                f"₹{CropState.total_harvest_income.to_string()}",
            ),
            metric_card(
                "trending-up",
                "Profitability",
                f"₹{CropState.profitability.to_string()}",
            ),
            class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6",
        ),
        rx.el.h3("Expense Breakdown", class_name="font-semibold text-lg mb-4"),
        rx.el.div(
            rx.recharts.pie_chart(
                rx.recharts.graphing_tooltip(),
                rx.recharts.pie(
                    rx.foreach(
                        CropState.expense_breakdown,
                        lambda item, index: rx.recharts.cell(fill=item["fill"]),
                    ),
                    data_key="value",
                    data=CropState.expense_breakdown,
                    cx="50%",
                    cy="50%",
                    outer_radius=80,
                    label_line=False,
                    stroke="#ffffff",
                    stroke_width=2,
                ),
                width="100%",
                height=300,
            ),
            rx.el.div(
                rx.foreach(
                    CropState.expense_breakdown,
                    lambda item: rx.el.div(
                        rx.el.div(
                            class_name="h-3 w-3 rounded-full",
                            style={"backgroundColor": item["fill"]},
                        ),
                        rx.el.span(item["name"], class_name="text-sm text-stone-600"),
                        class_name="flex items-center gap-2",
                    ),
                ),
                class_name="flex flex-wrap justify-center gap-4 mt-4",
            ),
            class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
        ),
    )


def activity_history_tab_content() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Date", class_name="px-4 py-2 text-left"),
                    rx.el.th("Activity", class_name="px-4 py-2 text-left"),
                    rx.el.th("Cost", class_name="px-4 py-2 text-left"),
                    rx.el.th("Notes", class_name="px-4 py-2 text-left"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    CropState.current_crop["activities"],
                    lambda record: rx.el.tr(
                        rx.el.td(record["date"], class_name="px-4 py-2 border-t"),
                        rx.el.td(
                            record["activity_type"], class_name="px-4 py-2 border-t"
                        ),
                        rx.el.td(
                            f"₹{record['cost'].to_string()}",
                            class_name="px-4 py-2 border-t",
                        ),
                        rx.el.td(record["notes"], class_name="px-4 py-2 border-t"),
                    ),
                )
            ),
            class_name="w-full text-sm",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def harvest_records_tab_content() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Date", class_name="px-4 py-2 text-left"),
                    rx.el.th("Quantity", class_name="px-4 py-2 text-left"),
                    rx.el.th("Income", class_name="px-4 py-2 text-left"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    CropState.current_crop["harvests"],
                    lambda record: rx.el.tr(
                        rx.el.td(record["date"], class_name="px-4 py-2 border-t"),
                        rx.el.td(
                            f"{record['quantity'].to_string()} {record['unit']}",
                            class_name="px-4 py-2 border-t",
                        ),
                        rx.el.td(
                            f"₹{record['income'].to_string()}",
                            class_name="px-4 py-2 border-t",
                        ),
                    ),
                )
            ),
            class_name="w-full text-sm",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def crop_profile_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.image(
                    src=CropState.current_crop["image_url"],
                    class_name="h-24 w-24 rounded-lg shadow-md border-2 border-white object-cover",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            CropState.current_crop["name"],
                            class_name="text-3xl font-bold text-stone-800",
                        ),
                        status_badge(CropState.current_crop["status"]),
                        class_name="flex items-center gap-3",
                    ),
                    rx.el.p(
                        f"Field: {CropState.current_crop['field_name']}",
                        class_name="text-stone-600",
                    ),
                    class_name="mt-2",
                ),
                class_name="flex items-center space-x-6",
            ),
            rx.el.div(
                action_button(
                    "plus",
                    "Add Activity",
                    lambda: CropState.toggle_add_activity_dialog(True),
                ),
                action_button(
                    "package",
                    "Add Harvest",
                    lambda: CropState.toggle_add_harvest_dialog(True),
                ),
                action_button(
                    "pencil", "Edit Details", rx.toast.info("Edit not yet implemented.")
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-center justify-between mb-6",
        ),
        profile_tabs(),
        rx.el.div(
            rx.match(
                CropState.profile_active_tab,
                ("Overview", overview_tab_content()),
                ("Activity History", activity_history_tab_content()),
                ("Harvest Records", harvest_records_tab_content()),
                rx.el.p("Select a tab"),
            ),
            class_name="mt-6",
        ),
        add_activity_dialog(),
        add_harvest_dialog(),
    )


def crop_profile_page() -> rx.Component:
    return dashboard_layout(
        rx.cond(
            CropState.profile_loading,
            rx.el.div(class_name="h-24 w-24 bg-stone-200 rounded-lg animate-pulse"),
            rx.cond(
                CropState.current_crop,
                crop_profile_content(),
                rx.el.div(
                    rx.el.h2(
                        "Crop not found", class_name="text-2xl font-bold text-stone-800"
                    ),
                    rx.el.p(
                        "Could not find crop data for the given ID.",
                        class_name="text-stone-600",
                    ),
                    class_name="text-center py-20",
                ),
            ),
        ),
        "Crop Profile",
    )

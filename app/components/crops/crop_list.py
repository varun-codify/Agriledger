import reflex as rx

from app.components.common import BTN_PRIMARY, empty_state
from app.states.crop_state import CropState

CROP_STATUS_FILTERS = [
    ("all", "All"),
    ("Growing", "Growing"),
    ("Planted", "Planted"),
    ("Harvested", "Harvested"),
    ("Fallow", "Fallow"),
]


def status_filter_button(label: str, value: str) -> rx.Component:
    is_selected = CropState.status_filter == value
    return rx.el.button(
        label,
        on_click=lambda: CropState.set_status_filter(value),
        class_name=rx.cond(
            is_selected,
            "px-4 py-1.5 rounded-lg text-sm font-semibold bg-emerald-500 text-white transition-all active:scale-95 shadow-sm",
            "px-4 py-1.5 rounded-lg text-sm font-semibold bg-white text-stone-600 border border-stone-200 transition-all hover:bg-stone-50 active:scale-95 dark:bg-stone-800 dark:text-stone-300 dark:border-stone-600 dark:hover:bg-stone-700",
        ),
    )


def crop_summary_card(
    icon: str, label: str, value: rx.Var, color_class: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-7 w-7"),
            class_name=f"p-3 rounded-full {color_class}",
        ),
        rx.el.div(
            rx.el.p(value, class_name="text-2xl font-bold text-stone-800 dark:text-stone-100"),
            rx.el.p(label, class_name="text-sm text-stone-500 dark:text-stone-400"),
            class_name="ml-4",
        ),
        class_name="flex items-center bg-white p-4 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700",
    )


def crop_card(crop: rx.Var[dict]) -> rx.Component:
    status = crop["status"]
    return rx.el.a(
        rx.el.div(
            rx.image(
                src=crop["image_url"],
                class_name="w-full h-32 object-cover rounded-t-2xl bg-stone-100",
            ),
            rx.el.div(
                rx.el.p(
                    crop["name"], class_name="font-bold text-lg text-stone-800 dark:text-stone-100 truncate"
                ),
                rx.el.div(
                    rx.el.span(
                        crop["field_name"],
                        class_name="text-xs font-mono px-2 py-1 bg-stone-100 text-stone-600 dark:bg-stone-800 dark:text-stone-300 rounded-md",
                    ),
                    rx.el.span(
                        status,
                        class_name=rx.match(
                            status,
                            (
                                "Growing",
                                "text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-800",
                            ),
                            (
                                "Harvested",
                                "text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800",
                            ),
                            (
                                "Planted",
                                "text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-800",
                            ),
                            (
                                "Fallow",
                                "text-xs px-2 py-1 rounded-full bg-stone-100 text-stone-600 dark:bg-stone-800 dark:text-stone-300",
                            ),
                            "text-xs px-2 py-1 rounded-full bg-stone-100 text-stone-600 dark:bg-stone-800 dark:text-stone-300",
                        ),
                    ),
                    class_name="flex items-center justify-between mt-2",
                ),
                class_name="p-4",
            ),
        ),
        href=f"/crops/{crop['id']}",
        class_name="bg-white rounded-2xl shadow-sm border border-stone-100 hover:shadow-lg hover:-translate-y-1 transition-all dark:bg-stone-900 dark:border-stone-700",
    )


def add_crop_dialog() -> rx.Component:
    return rx.cond(
        CropState.show_add_crop_dialog,
        rx.el.div(
            rx.el.div(
                on_click=lambda: CropState.toggle_add_crop_dialog(False),
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 al-fade-in",
            ),
            rx.el.div(
                rx.el.h2(
                    "Add New Crop", class_name="text-2xl font-bold text-stone-800 dark:text-stone-100"
                ),
                rx.el.p(
                    "Enter the details for your new crop entry.",
                    class_name="text-stone-500 text-sm dark:text-stone-400 mb-6 dark:text-stone-400",
                ),
                rx.cond(
                    CropState.add_crop_error != "",
                    rx.el.div(
                        rx.icon(
                            "triangle-alert", class_name="h-4 w-4 mr-2 flex-shrink-0"
                        ),
                        CropState.add_crop_error,
                        class_name="flex items-start text-red-600 text-sm bg-red-50 border border-red-200 p-3 rounded-lg mb-4",
                    ),
                    None,
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label("Crop Name", class_name="text-sm font-medium dark:text-stone-200"),
                        rx.el.input(
                            name="name",
                            placeholder="e.g., Corn, Wheat, Soybeans",
                            class_name="mt-1 w-full p-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        rx.el.label(
                            "Field Name/Identifier", class_name="text-sm font-medium dark:text-stone-200"
                        ),
                        rx.el.input(
                            name="field_name",
                            placeholder="e.g., Field A, North-West Patch",
                            class_name="mt-1 w-full p-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        rx.el.label("Planting Date", class_name="text-sm font-medium dark:text-stone-200"),
                        rx.el.input(
                            name="planting_date",
                            type="date",
                            default_value=CropState.current_dialog_date,
                            class_name="mt-1 w-full p-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        rx.el.label(
                            "Initial Cost (Optional)", class_name="text-sm font-medium dark:text-stone-200"
                        ),
                        rx.el.input(
                            name="initial_cost",
                            type="number",
                            step="0.01",
                            placeholder="e.g., 500.00 for seeds",
                            class_name="mt-1 w-full p-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=lambda: CropState.toggle_add_crop_dialog(False),
                            type="button",
                            class_name="w-full py-2 min-h-[40px] rounded-lg bg-stone-200 text-stone-800 font-semibold transition-all hover:bg-stone-300 active:scale-[0.98] dark:bg-stone-700 dark:text-stone-100 dark:hover:bg-stone-600",
                        ),
                        rx.el.button(
                            "Add Crop",
                            type="submit",
                            class_name=f"w-full py-2 min-h-[40px] {BTN_PRIMARY}",
                        ),
                        class_name="flex gap-4 mt-6",
                    ),
                    on_submit=CropState.add_crop,
                ),
                class_name="al-modal-in bg-white dark:bg-stone-900 p-8 rounded-2xl shadow-xl w-full max-w-2xl z-50 max-h-[90vh] overflow-y-auto border border-stone-100 dark:border-stone-700",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def crop_management_page() -> rx.Component:
    """The main page for managing all crops."""
    return rx.el.div(
        rx.el.div(
            crop_summary_card(
                "sprout",
                "Total Crops",
                CropState.crops_list.length(),
                "bg-emerald-100 text-emerald-600",
            ),
            crop_summary_card(
                "tractor",
                "Growing Now",
                CropState.growing_count,
                "bg-blue-100 text-blue-600",
            ),
            crop_summary_card(
                "indian-rupee",
                "Total Investment",
                f"₹{CropState.total_investment}",
                "bg-yellow-100 text-yellow-600",
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6",
        ),
        rx.el.div(
            rx.el.div(
                *[
                    status_filter_button(label, value)
                    for value, label in CROP_STATUS_FILTERS
                ],
                class_name="flex gap-2 flex-wrap",
            ),
            rx.el.div(
                rx.el.a(
                    rx.icon("scan-eye", class_name="h-4 w-4 mr-2 text-emerald-600"),
                    "AI Leaf Disease Scanner",
                    href="/disease-scanner",
                    class_name="flex items-center bg-emerald-50 text-emerald-700 border border-emerald-300 hover:bg-emerald-100 px-4 py-2 rounded-lg font-semibold transition-all shadow-sm dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800 dark:hover:bg-emerald-900",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-2"),
                    "Add New Crop",
                    on_click=lambda: CropState.toggle_add_crop_dialog(True),
                    class_name=f"flex items-center px-4 py-2 min-h-[40px] {BTN_PRIMARY}",
                ),
                class_name="flex items-center gap-3 flex-wrap",
            ),
            class_name="flex items-center justify-between mb-6 flex-wrap gap-4",
        ),
        rx.cond(
            CropState.filtered_crops.length() == 0,
            empty_state(
                "sprout",
                "No crops match this filter",
                "Try a different status filter or add your first crop.",
            ),
            rx.el.div(
                rx.foreach(CropState.filtered_crops, crop_card),
                class_name="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6",
            ),
        ),
        add_crop_dialog(),
    )

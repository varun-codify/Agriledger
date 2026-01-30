import reflex as rx
from app.states.cattle_state import CattleState


def summary_stat_card(
    icon: str, label: str, value: rx.Var, color_class: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-7 w-7"),
            class_name=f"p-3 rounded-full {color_class}",
        ),
        rx.el.div(
            rx.el.p(value, class_name="text-2xl font-bold text-stone-800"),
            rx.el.p(label, class_name="text-sm text-stone-500"),
            class_name="ml-4",
        ),
        class_name="flex items-center bg-white p-4 rounded-2xl shadow-sm border border-stone-100",
    )


def animal_type_badge(animal_type: rx.Var[str]) -> rx.Component:
    color_map = {
        "cow": "bg-blue-100 text-blue-800",
        "buffalo": "bg-gray-200 text-gray-800",
        "sheep": "bg-green-100 text-green-800",
        "goat": "bg-orange-100 text-orange-800",
        "hen": "bg-red-100 text-red-800",
        "cock": "bg-red-200 text-red-900",
        "chick": "bg-yellow-100 text-yellow-800",
    }
    return rx.el.span(
        animal_type.capitalize(),
        class_name=f"text-xs px-2 py-1 rounded-full {rx.match(animal_type, *color_map.items(), 'bg-stone-100 text-stone-600')}",
    )


def juvenile_badge(animal_type: rx.Var[str]) -> rx.Component:
    badge_text = rx.match(
        animal_type, ("sheep", "Lamb"), ("goat", "Kid"), ("chick", "Chick"), "Juvenile"
    )
    return rx.el.span(
        badge_text,
        class_name="text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-800 font-semibold",
    )


def cattle_card(cattle: rx.Var[dict]) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.image(
                src=cattle["image_url"],
                class_name="w-full h-32 object-cover rounded-t-2xl",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        cattle["name"],
                        class_name="font-bold text-lg text-stone-800 truncate",
                    ),
                    rx.cond(
                        cattle["is_juvenile"],
                        juvenile_badge(cattle["animal_type"]),
                        None,
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(
                    animal_type_badge(cattle["animal_type"]),
                    rx.el.span(
                        f"#{cattle['tag_number']}",
                        class_name="text-xs font-mono px-2 py-1 bg-stone-100 text-stone-600 rounded-md",
                    ),
                    class_name="flex items-center justify-between mt-2",
                ),
                class_name="p-4",
            ),
        ),
        href=f"/cattle/{cattle['id']}",
        class_name="bg-white rounded-2xl shadow-sm border border-stone-100 hover:shadow-lg hover:-translate-y-1 transition-all",
    )


def add_cattle_dialog() -> rx.Component:
    return rx.cond(
        CattleState.show_add_cattle_dialog,
        rx.el.div(
            rx.el.div(
                on_click=lambda: CattleState.toggle_add_cattle_dialog(False),
                class_name="fixed inset-0 bg-black/50 z-40",
            ),
            rx.el.div(
                rx.el.h2(
                    "Add New Animal", class_name="text-2xl font-bold text-stone-800"
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label("Name", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="name", class_name="mt-1 w-full p-2 border rounded-md"
                        ),
                        rx.el.label("Tag Number", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="tag_number",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Animal Type", class_name="text-sm font-medium"),
                        rx.el.select(
                            "cow",
                            "buffalo",
                            "sheep",
                            "goat",
                            "hen",
                            "cock",
                            "chick",
                            name="animal_type",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Breed", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="breed", class_name="mt-1 w-full p-2 border rounded-md"
                        ),
                        rx.el.label("Age (years)", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="age",
                            type="number",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Weight (kg)", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="weight",
                            type="number",
                            step="0.1",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label(
                            "Purchase Price ($)", class_name="text-sm font-medium"
                        ),
                        rx.el.input(
                            name="purchase_price",
                            type="number",
                            step="0.01",
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.label("Purchase Date", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="purchase_date",
                            type="date",
                            default_value=CattleState.new_cattle_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Is Juvenile?",
                                rx.el.input(
                                    type="checkbox",
                                    name="is_juvenile",
                                    class_name="ml-2",
                                ),
                                class_name="flex items-center text-sm font-medium",
                            ),
                            class_name="col-span-2",
                        ),
                        class_name="grid grid-cols-2 gap-4",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            type="button",
                            on_click=lambda: CattleState.toggle_add_cattle_dialog(
                                False
                            ),
                            class_name="w-full py-2 rounded-lg bg-stone-200 text-stone-800 font-semibold",
                        ),
                        rx.el.button(
                            "Add Animal",
                            type="submit",
                            class_name="w-full py-2 rounded-lg bg-emerald-500 text-white font-semibold",
                        ),
                        class_name="flex gap-4 mt-6",
                    ),
                    on_submit=CattleState.add_cattle,
                    reset_on_submit=True,
                ),
                class_name="bg-white p-8 rounded-2xl shadow-xl w-full max-w-2xl z-50",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def animal_filter_button(label: str, filter_value: str) -> rx.Component:
    is_selected = CattleState.animal_type_filter == filter_value
    return rx.el.button(
        label,
        on_click=lambda: CattleState.set_animal_filter(filter_value),
        class_name=rx.cond(
            is_selected,
            "px-4 py-1.5 rounded-lg text-sm font-semibold bg-emerald-500 text-white",
            "px-4 py-1.5 rounded-lg text-sm font-semibold bg-white text-stone-600 border",
        ),
    )


def cattle_management_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            summary_stat_card(
                "git-fork",
                "Total Animals",
                CattleState.total_cattle,
                "bg-blue-100 text-blue-600",
            ),
            summary_stat_card(
                "dog", "Cows", CattleState.total_cows, "bg-blue-100 text-blue-600"
            ),
            summary_stat_card(
                "trophy",
                "Buffaloes",
                CattleState.total_buffaloes,
                "bg-gray-100 text-gray-600",
            ),
            summary_stat_card(
                "wheat",
                f"Sheep: {CattleState.total_sheep} / {CattleState.total_lambs} lambs",
                "",
                "bg-green-100 text-green-600",
            ),
            summary_stat_card(
                "trophy",
                f"Goats: {CattleState.total_goats} / {CattleState.total_kids} kids",
                "",
                "bg-orange-100 text-orange-600",
            ),
            summary_stat_card(
                "bird",
                f"Poultry: {CattleState.total_poultry}",
                "",
                "bg-red-100 text-red-600",
            ),
            class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-6",
        ),
        rx.el.div(
            rx.el.div(
                animal_filter_button("All", "all"),
                animal_filter_button("Cows", "cow"),
                animal_filter_button("Buffaloes", "buffalo"),
                animal_filter_button("Sheep", "sheep"),
                animal_filter_button("Goats", "goat"),
                animal_filter_button("Poultry", "poultry"),
                class_name="flex gap-2 flex-wrap",
            ),
            rx.el.button(
                rx.icon("plus", class_name="h-4 w-4 mr-2"),
                "Add New Animal",
                on_click=lambda: CattleState.toggle_add_cattle_dialog(True),
                class_name="flex items-center bg-emerald-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-emerald-600 transition-all",
            ),
            class_name="flex items-center justify-between mb-6",
        ),
        rx.el.div(
            rx.foreach(CattleState.filtered_cattle, cattle_card),
            class_name="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6",
        ),
        add_cattle_dialog(),
    )
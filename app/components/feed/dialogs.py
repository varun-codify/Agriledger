"""Feed module dialogs: add feed type, add stock, create feeding plan.

Uses the shared animated modal shell from ``common``.
"""

import reflex as rx

from app.components.common import BTN_PRIMARY, BTN_SECONDARY, modal_shell
from app.states.feed_state import FeedState, PLAN_CATEGORIES

UNITS = ["kg", "bundles", "bags"]
CATEGORIES = ["Concentrate", "Home Grown"]


# ── Add feed type dialog ─────────────────────────────────────────────

def feed_type_dialog() -> rx.Component:
    return modal_shell(
        rx.el.div(
            rx.el.h2("Add Feed Type", class_name="text-xl font-bold text-stone-800 dark:text-stone-100"),
            rx.el.p(
                "e.g. Maize Bran, Banana Stem, Custom Mix",
                class_name="text-sm text-stone-500 dark:text-stone-400 mt-1",
            ),
            rx.el.div(
                rx.el.label(
                    "Feed Name", class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300"
                ),
                rx.el.input(
                    placeholder="e.g. Maize Bran",
                    value=FeedState.new_feed_name,
                    on_change=FeedState.set_new_feed_name,
                    class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                rx.el.label(
                    "Category",
                    class_name="block text-sm font-medium text-stone-700 mb-1 mt-4 dark:text-stone-300",
                ),
                rx.el.select(
                    rx.foreach(
                        CATEGORIES,
                        lambda c: rx.el.option(c, value=c),
                    ),
                    value=FeedState.new_feed_category,
                    on_change=FeedState.set_new_feed_category,
                    class_name="w-full px-3 py-2 border rounded-md bg-white dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                rx.el.label(
                    "Unit", class_name="block text-sm font-medium text-stone-700 mb-1 mt-4 dark:text-stone-300"
                ),
                rx.el.select(
                    rx.foreach(
                        UNITS,
                        lambda u: rx.el.option(u, value=u),
                    ),
                    value=FeedState.new_feed_unit,
                    on_change=FeedState.set_new_feed_unit,
                    class_name="w-full px-3 py-2 border rounded-md bg-white dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                rx.el.label(
                    "Cost per Unit (₹)",
                    class_name="block text-sm font-medium text-stone-700 mb-1 mt-4 dark:text-stone-300",
                ),
                rx.el.input(
                    placeholder="e.g. 30",
                    value=FeedState.new_feed_cost_str,
                    on_change=FeedState.set_new_feed_cost,
                    input_mode="decimal",
                    class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                class_name="my-6 space-y-1",
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    on_click=lambda: FeedState.toggle_feed_type_dialog(False),
                    class_name=f"px-4 py-2 {BTN_SECONDARY}",
                ),
                rx.el.button(
                    "Add Feed Type",
                    on_click=FeedState.add_feed_type,
                    class_name=f"px-4 py-2 {BTN_PRIMARY}",
                ),
                class_name="flex justify-end gap-4",
            ),
        ),
        FeedState.show_feed_type_dialog,
        lambda: FeedState.toggle_feed_type_dialog(False),
    )


# ── Add stock dialog ─────────────────────────────────────────────────

def stock_dialog() -> rx.Component:
    return modal_shell(
        rx.el.div(
            rx.el.h2("Add Feed Stock", class_name="text-xl font-bold text-stone-800 dark:text-stone-100"),
            rx.el.p(
                "Record a feed purchase / stock addition.",
                class_name="text-sm text-stone-500 dark:text-stone-400 mt-1",
            ),
            rx.el.div(
                rx.el.label(
                    "Feed Type",
                    class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                ),
                rx.el.select(
                    rx.foreach(
                        FeedState.feed_type_options,
                        lambda opt: rx.el.option(opt["label"], value=opt["id"]),
                    ),
                    value=FeedState.stock_feed_type_id,
                    on_change=FeedState.set_stock_feed_type_id,
                    class_name="w-full px-3 py-2 border rounded-md bg-white dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Quantity",
                            class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                        ),
                        rx.el.input(
                            placeholder="e.g. 50",
                            value=FeedState.stock_quantity_str,
                            on_change=FeedState.set_stock_quantity,
                            input_mode="decimal",
                            class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        class_name="flex-1",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Unit", class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300"
                        ),
                        rx.el.select(
                            rx.foreach(
                                UNITS,
                                lambda u: rx.el.option(u, value=u),
                            ),
                            value=FeedState.stock_unit,
                            on_change=FeedState.set_stock_unit,
                            class_name="w-full px-3 py-2 border rounded-md bg-white dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        class_name="w-28",
                    ),
                    class_name="flex gap-4 mt-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Purchase Date",
                            class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                        ),
                        rx.el.input(
                            type="date",
                            value=FeedState.stock_purchase_date,
                            on_change=FeedState.set_stock_purchase_date,
                            class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        class_name="flex-1",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Expiry Date",
                            class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                        ),
                        rx.el.input(
                            type="date",
                            value=FeedState.stock_expiry_date,
                            on_change=FeedState.set_stock_expiry_date,
                            class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        class_name="flex-1",
                    ),
                    class_name="flex gap-4 mt-4",
                ),
                rx.el.label(
                    "Supplier", class_name="block text-sm font-medium text-stone-700 mb-1 mt-4 dark:text-stone-300"
                ),
                rx.el.input(
                    placeholder="e.g. Annai Feeds",
                    value=FeedState.stock_supplier,
                    on_change=FeedState.set_stock_supplier,
                    class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                rx.el.label(
                    "Total Cost (₹)",
                    class_name="block text-sm font-medium text-stone-700 mb-1 mt-4 dark:text-stone-300",
                ),
                rx.el.input(
                    placeholder="e.g. 1400",
                    value=FeedState.stock_cost_str,
                    on_change=FeedState.set_stock_cost,
                    input_mode="decimal",
                    class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                class_name="my-6 space-y-1",
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    on_click=lambda: FeedState.toggle_stock_dialog(False),
                    class_name=f"px-4 py-2 {BTN_SECONDARY}",
                ),
                rx.el.button(
                    "Save Stock",
                    on_click=FeedState.add_stock,
                    class_name=f"px-4 py-2 {BTN_PRIMARY}",
                ),
                class_name="flex justify-end gap-4",
            ),
        ),
        FeedState.show_stock_dialog,
        lambda: FeedState.toggle_stock_dialog(False),
    )


# ── Create feeding plan dialog ───────────────────────────────────────

def plan_dialog() -> rx.Component:
    return modal_shell(
        rx.el.div(
            rx.el.h2("Create Feeding Plan", class_name="text-xl font-bold text-stone-800 dark:text-stone-100"),
            rx.el.p(
                "Plan daily feed quantities per animal group.",
                class_name="text-sm text-stone-500 dark:text-stone-400 mt-1",
            ),
            rx.el.div(
                rx.el.label(
                    "Animal Group",
                    class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                ),
                rx.el.select(
                    rx.foreach(
                        PLAN_CATEGORIES,
                        lambda c: rx.el.option(c, value=c),
                    ),
                    value=FeedState.plan_category,
                    on_change=FeedState.set_plan_category,
                    class_name="w-full px-3 py-2 border rounded-md bg-white dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Morning Feed",
                            class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                        ),
                        rx.el.select(
                            rx.foreach(
                                FeedState.feed_type_options,
                                lambda opt: rx.el.option(opt["label"], value=opt["id"]),
                            ),
                            value=FeedState.plan_morning_feed_id,
                            on_change=FeedState.set_plan_morning_feed_id,
                            class_name="w-full px-3 py-2 border rounded-md bg-white dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        class_name="flex-1",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Qty", class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300"
                        ),
                        rx.el.input(
                            placeholder="e.g. 2",
                            value=FeedState.plan_morning_qty_str,
                            on_change=FeedState.set_plan_morning_qty,
                            input_mode="decimal",
                            class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        class_name="w-24",
                    ),
                    class_name="flex gap-4 mt-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Evening Feed",
                            class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                        ),
                        rx.el.select(
                            rx.foreach(
                                FeedState.feed_type_options,
                                lambda opt: rx.el.option(opt["label"], value=opt["id"]),
                            ),
                            value=FeedState.plan_evening_feed_id,
                            on_change=FeedState.set_plan_evening_feed_id,
                            class_name="w-full px-3 py-2 border rounded-md bg-white dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        class_name="flex-1",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Qty", class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300"
                        ),
                        rx.el.input(
                            placeholder="e.g. 2",
                            value=FeedState.plan_evening_qty_str,
                            on_change=FeedState.set_plan_evening_qty,
                            input_mode="decimal",
                            class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                        ),
                        class_name="w-24",
                    ),
                    class_name="flex gap-4 mt-4",
                ),
                rx.el.label(
                    "Mineral Supplements",
                    class_name="block text-sm font-medium text-stone-700 mb-1 mt-4 dark:text-stone-300",
                ),
                rx.el.input(
                    placeholder="e.g. 50g mineral mixture daily",
                    value=FeedState.plan_minerals,
                    on_change=FeedState.set_plan_minerals,
                    class_name="w-full px-3 py-2 border rounded-md dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100 min-h-[40px]",
                ),
                rx.el.label(
                    "Water Reminder",
                    class_name="block text-sm font-medium text-stone-700 mb-2 mt-4 dark:text-stone-300",
                ),
                rx.el.div(
                    rx.el.button(
                        "Yes",
                        on_click=lambda: FeedState.set_plan_water_reminder(True),
                        class_name=rx.cond(
                            FeedState.plan_water_reminder,
                            "flex-1 px-4 py-2 rounded-lg font-semibold bg-emerald-500 text-white",
                            "flex-1 px-4 py-2 rounded-lg font-semibold bg-stone-200 text-stone-600 dark:bg-stone-700 dark:text-stone-300",
                        ),
                    ),
                    rx.el.button(
                        "No",
                        on_click=lambda: FeedState.set_plan_water_reminder(False),
                        class_name=rx.cond(
                            FeedState.plan_water_reminder,
                            "flex-1 px-4 py-2 rounded-lg font-semibold bg-stone-200 text-stone-600 dark:bg-stone-700 dark:text-stone-300",
                            "flex-1 px-4 py-2 rounded-lg font-semibold bg-emerald-500 text-white",
                        ),
                    ),
                    class_name="flex gap-3",
                ),
                class_name="my-6 space-y-1",
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    on_click=lambda: FeedState.toggle_plan_dialog(False),
                    class_name=f"px-4 py-2 {BTN_SECONDARY}",
                ),
                rx.el.button(
                    "Create Plan",
                    on_click=FeedState.create_plan,
                    class_name=f"px-4 py-2 {BTN_PRIMARY}",
                ),
                class_name="flex justify-end gap-4",
            ),
        ),
        FeedState.show_plan_dialog,
        lambda: FeedState.toggle_plan_dialog(False),
    )

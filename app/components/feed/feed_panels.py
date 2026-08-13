"""Feed Intelligence panels.

Farmer-first UI: big buttons, minimal typing, icons over text.
Daily feeding is a 3-tap flow — tap animal → tap feed → tap quantity → Record.
"""

import reflex as rx

from app.states.cattle_state import CattleState
from app.states.feed_state import (
    FeedState,
    MILK_PRICE_PER_LITER,
    PLAN_CATEGORIES,
    SIM_CHANGE_OPTIONS,
)

# ── Section shell ────────────────────────────────────────────────────

def section(title: str, subtitle: str, icon: str, content, id: str) -> rx.Component:
    """A titled white card section with anchor id for quick-nav."""
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-emerald-500"),
            rx.el.div(
                rx.el.h2(title, class_name="text-xl font-bold text-stone-800"),
                rx.el.p(subtitle, class_name="text-sm text-stone-500"),
                class_name="ml-3",
            ),
            class_name="flex items-center mb-5",
        ),
        content,
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 scroll-mt-24",
        id=id,
    )


# ── Overview cards (spec: Dashboard section) ─────────────────────────

def feed_card(card: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(card["icon"], class_name="text-2xl"),
            class_name=f"w-11 h-11 rounded-xl flex items-center justify-center {card['color']}",
        ),
        rx.el.div(
            rx.el.p(card["title"], class_name="text-xs font-medium text-stone-500 mt-3"),
            rx.el.p(card["value"], class_name="text-xl font-bold text-stone-800 truncate"),
            rx.el.p(card["sub"], class_name="text-xs text-stone-400 truncate"),
            class_name="flex-1 min-w-0",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 flex gap-4 items-start min-w-0",
    )


def feed_overview_cards() -> rx.Component:
    return rx.el.div(
        rx.foreach(FeedState.dashboard_cards, feed_card),
        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4",
    )


# ── Daily feeding (spec: Daily Feeding + UX principles) ──────────────

def animal_chip(animal: rx.Var[dict]) -> rx.Component:
    return rx.el.button(
        rx.image(
            src=animal["image_url"],
            class_name="w-12 h-12 rounded-full object-cover border-2 mx-auto",
            style={"borderColor": rx.cond(
                FeedState.feeding_animal_id == animal["id"], "#10b981", "#e7e5e4"
            )},
        ),
        rx.el.span(
            animal["name"],
            class_name="text-xs font-semibold truncate w-full text-center",
        ),
        on_click=lambda: FeedState.set_feeding_animal_id(animal["id"]),
        class_name=rx.cond(
            FeedState.feeding_animal_id == animal["id"],
            "flex flex-col gap-1 p-2 rounded-xl bg-emerald-50 border-2 border-emerald-500 w-24 flex-shrink-0",
            "flex flex-col gap-1 p-2 rounded-xl bg-stone-50 border-2 border-transparent hover:bg-stone-100 w-24 flex-shrink-0",
        ),
    )


def feed_type_chip(ft: rx.Var[dict]) -> rx.Component:
    return rx.el.button(
        rx.el.span(ft["name"], class_name="font-semibold text-sm"),
        rx.el.span(
            f"{ft['unit']} · ₹{ft['cost_per_unit']:.0f}",
            class_name="text-xs text-stone-500",
        ),
        on_click=lambda: FeedState.set_feeding_feed_type_id(ft["id"]),
        class_name=rx.cond(
            FeedState.feeding_feed_type_id == ft["id"],
            "flex flex-col items-start px-4 py-3 rounded-xl bg-emerald-500 text-white border-2 border-emerald-600",
            "flex flex-col items-start px-4 py-3 rounded-xl bg-stone-50 text-stone-800 border-2 border-transparent hover:bg-stone-100",
        ),
    )


def keypad_button(key: str) -> rx.Component:
    return rx.el.button(
        rx.cond(
            key == "del",
            rx.icon("delete", class_name="h-6 w-6"),
            key,
        ),
        on_click=lambda: FeedState.handle_feeding_keypad(key),
        class_name=(
            "h-14 rounded-xl bg-stone-100 text-stone-800 text-xl font-bold "
            "hover:bg-emerald-100 active:scale-95 transition-all"
        ),
    )


def daily_feeding_panel() -> rx.Component:
    return section(
        "Daily Feeding",
        "Tap animal → tap feed → quantity → Record. 3 taps, done.",
        "utensils-crossed",
        rx.el.div(
            # Step 1: animal
            rx.cond(
                CattleState.cattle_list.length() == 0,
                rx.el.div(
                    rx.el.p(
                        "No animals yet. Add animals in the Animal Management page first.",
                        class_name="text-sm text-stone-500",
                    ),
                    rx.el.a(
                        "Go to Animals",
                        href="/cattle",
                        class_name="mt-2 inline-block text-sm font-semibold text-emerald-600",
                    ),
                    class_name="bg-stone-50 rounded-xl p-4 text-center",
                ),
                rx.el.div(
                    rx.foreach(CattleState.cattle_list, animal_chip),
                    class_name="flex gap-3 overflow-x-auto pb-2",
                ),
            ),
            # Step 2: feed type
            rx.el.p(
                "Choose Feed",
                class_name="text-sm font-semibold text-stone-600 mt-5 mb-2",
            ),
            rx.el.div(
                rx.foreach(FeedState.feed_types, feed_type_chip),
                class_name="flex flex-wrap gap-2",
            ),
            # Step 3: time + quantity + record
            rx.el.div(
                rx.el.p(
                    "Time of Day",
                    class_name="text-sm font-semibold text-stone-600 mt-5 mb-2",
                ),
                rx.el.div(
                    rx.el.button(
                        "🌅 Morning",
                        on_click=lambda: FeedState.set_feeding_time_of_day("Morning"),
                        class_name=rx.cond(
                            FeedState.feeding_time_of_day == "Morning",
                            "flex-1 px-4 py-3 rounded-xl bg-amber-500 text-white font-bold text-lg",
                            "flex-1 px-4 py-3 rounded-xl bg-stone-100 text-stone-600 font-bold text-lg hover:bg-stone-200",
                        ),
                    ),
                    rx.el.button(
                        "🌇 Evening",
                        on_click=lambda: FeedState.set_feeding_time_of_day("Evening"),
                        class_name=rx.cond(
                            FeedState.feeding_time_of_day == "Evening",
                            "flex-1 px-4 py-3 rounded-xl bg-indigo-500 text-white font-bold text-lg",
                            "flex-1 px-4 py-3 rounded-xl bg-stone-100 text-stone-600 font-bold text-lg hover:bg-stone-200",
                        ),
                    ),
                    class_name="flex gap-3",
                ),
                # Big quantity display
                rx.el.div(
                    rx.el.p(
                        FeedState.feeding_qty_str,
                        class_name="text-5xl font-extrabold text-emerald-600 text-center",
                    ),
                    rx.el.div(
                        rx.foreach(
                            ["+0.5", "+1", "+2", "+5"],
                            lambda q: rx.el.button(
                                q,
                                on_click=lambda: FeedState.quick_add_feeding_qty(q),
                                class_name="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 font-semibold text-sm hover:bg-emerald-100",
                            ),
                        ),
                        class_name="flex gap-2 justify-center mt-2",
                    ),
                    class_name="bg-stone-50 rounded-2xl p-6 mt-5",
                ),
                # Keypad
                rx.el.div(
                    rx.foreach(
                        ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "del"],
                        keypad_button,
                    ),
                    class_name="grid grid-cols-3 gap-3 mt-4",
                ),
                rx.el.input(
                    placeholder="Notes (optional)",
                    value=FeedState.feeding_notes,
                    on_change=FeedState.set_feeding_notes,
                    class_name="w-full px-4 py-3 rounded-xl border border-stone-200 mt-4",
                ),
                rx.cond(
                    FeedState.feeding_success != "",
                    rx.el.div(
                        FeedState.feeding_success,
                        class_name="mt-4 px-4 py-3 rounded-xl bg-emerald-50 text-emerald-700 font-semibold text-center",
                    ),
                    None,
                ),
                rx.el.button(
                    rx.icon("check", class_name="h-6 w-6 mr-2"),
                    "Record Feeding",
                    on_click=FeedState.record_feeding,
                    class_name="w-full mt-4 bg-emerald-500 text-white py-4 rounded-xl font-bold text-lg hover:bg-emerald-600 active:scale-[0.99] transition-all shadow-md",
                ),
            ),
        ),
        "feed-feeding",
    )


# ── Inventory (spec: Feed Inventory) ─────────────────────────────────

def stock_status_badge(stock: rx.Var[dict]) -> rx.Component:
    return rx.cond(
        stock["quantity"] <= 0,
        rx.el.span(
            "🔴 Out of Stock",
            class_name="px-2 py-1 rounded-full bg-red-50 text-red-600 text-xs font-bold",
        ),
        rx.cond(
            stock["quantity"] < 10,
            rx.el.span(
                "🟡 Low Stock",
                class_name="px-2 py-1 rounded-full bg-amber-50 text-amber-600 text-xs font-bold",
            ),
            rx.el.span(
                "🟢 Sufficient",
                class_name="px-2 py-1 rounded-full bg-emerald-50 text-emerald-600 text-xs font-bold",
            ),
        ),
    )


def stock_card(stock: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(stock["feed_name"], class_name="font-bold text-stone-800"),
            stock_status_badge(stock),
            class_name="flex items-center justify-between gap-2",
        ),
        rx.el.p(
            f"{stock['quantity']} {stock['unit']}",
            class_name="text-2xl font-extrabold text-stone-800 mt-2",
        ),
        rx.el.div(
            rx.cond(
                stock["supplier"] != "",
                rx.el.p(
                    f"From {stock['supplier']}",
                    class_name="text-xs text-stone-500",
                ),
                None,
            ),
            rx.cond(
                stock["expiry_date"],
                rx.el.p(
                    f"Expires {stock['expiry_date']}",
                    class_name="text-xs text-orange-500",
                ),
                None,
            ),
            class_name="mt-1 space-y-0.5",
        ),
        class_name="bg-stone-50 p-4 rounded-xl border border-stone-100",
    )


def feed_type_card(ft: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.p(ft["name"], class_name="font-semibold text-stone-800 text-sm"),
        rx.el.span(
            rx.cond(
                ft["category"] == "Concentrate",
                "🧪 Concentrate",
                "🌾 Home Grown",
            ),
            class_name=rx.cond(
                ft["category"] == "Concentrate",
                "text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 font-medium",
                "text-xs px-2 py-0.5 rounded-full bg-green-50 text-green-600 font-medium",
            ),
        ),
        rx.el.p(
            f"₹{ft['cost_per_unit']:.0f} / {ft['unit']}",
            class_name="text-xs text-stone-500 mt-1",
        ),
        class_name="bg-white p-3 rounded-xl border border-stone-200 flex flex-col gap-1",
    )


def homegrown_crop_card(row: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span("🌾", class_name="text-2xl"),
            rx.el.div(
                rx.el.p(row["name"], class_name="font-bold text-stone-800 text-sm"),
                rx.el.p(
                    f"{row['harvested']} {row['unit']} harvested · {row['moved']} {row['unit']} in stock",
                    class_name="text-xs text-stone-500",
                ),
                class_name="flex-1 min-w-0",
            ),
            rx.cond(
                row["synced"],
                rx.el.span(
                    "✓ In stock",
                    class_name="text-xs px-2 py-1 rounded-full bg-emerald-50 text-emerald-600 font-bold flex-shrink-0",
                ),
                rx.el.span(
                    "⏳ Pending sync",
                    class_name="text-xs px-2 py-1 rounded-full bg-amber-50 text-amber-600 font-bold flex-shrink-0",
                ),
            ),
            class_name="flex items-center gap-3",
        ),
        rx.cond(
            row["available"],
            rx.el.p(
                f"{row['delta']} {row['unit']} new — will move automatically on next page load.",
                class_name="text-xs text-orange-600 mt-1",
            ),
            None,
        ),
        class_name="bg-white p-3 rounded-xl border border-stone-200",
    )


def homegrown_crops_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Home-Grown Crops → Feed Stock",
                    class_name="text-sm font-semibold text-stone-600",
                ),
                rx.el.p(
                    "Fodder harvests move into feed stock automatically on page load.",
                    class_name="text-xs text-stone-400",
                ),
                class_name="flex-1",
            ),
            rx.el.button(
                rx.icon("refresh-ccw", class_name="h-4 w-4 mr-1"),
                "Sync Now",
                on_click=FeedState.auto_sync_homegrown_crops,
                class_name="flex items-center text-xs font-bold px-3 py-1.5 rounded-lg bg-emerald-500 text-white hover:bg-emerald-600",
            ),
            class_name="flex items-center gap-3",
        ),
        rx.cond(
            FeedState.homegrown_summary.length() == 0,
            rx.el.p(
                "Record a harvest on a fodder crop (e.g. Cholam, sorghum, straw) and it will appear here and move into feed stock automatically.",
                class_name="text-xs text-stone-500 text-center py-4 bg-stone-50 rounded-xl mt-3",
            ),
            rx.el.div(
                rx.foreach(FeedState.homegrown_summary, homegrown_crop_card),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3",
            ),
        ),
        class_name="mt-8",
    )


def inventory_panel() -> rx.Component:
    return section(
        "Feed Inventory & Types",
        "Track stock levels and feed types. Add stock whenever you buy feed.",
        "warehouse",
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Feed Types",
                    class_name="text-sm font-semibold text-stone-600 mb-2",
                ),
                rx.el.div(
                    rx.foreach(FeedState.feed_types, feed_type_card),
                    class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="h-4 w-4 mr-1"),
                    "Add Feed Type",
                    on_click=lambda: FeedState.toggle_feed_type_dialog(True),
                    class_name="mt-3 flex items-center text-sm font-semibold text-emerald-600 hover:text-emerald-700",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Current Stock",
                        class_name="text-sm font-semibold text-stone-600 mb-2",
                    ),
                    rx.el.button(
                        rx.icon("plus", class_name="h-4 w-4 mr-1"),
                        "Add Stock",
                        on_click=lambda: FeedState.toggle_stock_dialog(True),
                        class_name="flex items-center text-sm font-semibold text-emerald-600 hover:text-emerald-700",
                    ),
                    class_name="flex items-center justify-between",
                ),
                rx.cond(
                    FeedState.inventory.length() == 0,
                    rx.el.div(
                        rx.el.p(
                            "No stock recorded yet. Add your first purchase.",
                            class_name="text-sm text-stone-500 text-center py-6",
                        ),
                        class_name="bg-stone-50 rounded-xl",
                    ),
                    rx.el.div(
                        rx.foreach(FeedState.inventory, stock_card),
                        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-3",
                    ),
                ),
            ),
            homegrown_crops_section(),
            class_name="space-y-8",
        ),
        "feed-inventory",
    )


# ── Feeding plans (spec: Feeding Plans) ──────────────────────────────

def plan_item(item: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.span(item["feed_name"], class_name="text-sm font-medium text-stone-700"),
        rx.el.span(
            f"{item['quantity']} {item['unit']}",
            class_name="text-sm font-bold text-stone-800",
        ),
        class_name="flex items-center justify-between py-1 border-b border-dashed border-stone-200 last:border-0",
    )


def plan_card(plan: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(plan["name"], class_name="font-bold text-stone-800"),
            rx.el.span(
                "💧 Water reminder",
                class_name=rx.cond(
                    plan["water_reminder"],
                    "text-xs px-2 py-0.5 rounded-full bg-sky-50 text-sky-600 font-medium",
                    "text-xs px-2 py-0.5 rounded-full bg-stone-100 text-stone-400 font-medium",
                ),
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.el.p("🌅 Morning", class_name="text-xs font-bold text-amber-600 mb-1"),
            rx.cond(
                plan["morning"].length() > 0,
                rx.foreach(plan["morning"], plan_item),
                rx.el.p("—", class_name="text-xs text-stone-400"),
            ),
            class_name="mt-3",
        ),
        rx.el.div(
            rx.el.p("🌇 Evening", class_name="text-xs font-bold text-indigo-600 mb-1"),
            rx.cond(
                plan["evening"].length() > 0,
                rx.foreach(plan["evening"], plan_item),
                rx.el.p("—", class_name="text-xs text-stone-400"),
            ),
            class_name="mt-3",
        ),
        rx.cond(
            plan["minerals"] != "",
            rx.el.div(
                rx.icon("pill", class_name="h-4 w-4 text-emerald-500"),
                rx.el.span(plan["minerals"], class_name="text-xs text-stone-600"),
                class_name="flex items-center gap-1 mt-3",
            ),
            None,
        ),
        rx.el.button(
            rx.icon("utensils-crossed", class_name="h-4 w-4 mr-1"),
            f"Feed All {plan['category']} Now",
            on_click=lambda: FeedState.bulk_feed_plan(plan["id"]),
            class_name="mt-3 w-full flex items-center justify-center text-xs font-bold px-3 py-2 rounded-lg bg-emerald-500 text-white hover:bg-emerald-600 transition-all",
        ),
        class_name="bg-stone-50 p-4 rounded-xl border border-stone-100",
    )


def feeding_plans_panel() -> rx.Component:
    return section(
        "Feeding Plans",
        "Standard daily rations for each animal group — calves to bulls.",
        "clipboard-list",
        rx.el.div(
            rx.cond(
                FeedState.feeding_plans.length() == 0,
                rx.el.p(
                    "No plans yet. Create one to standardize your feeding routine.",
                    class_name="text-sm text-stone-500 text-center py-6 bg-stone-50 rounded-xl",
                ),
                rx.el.div(
                    rx.foreach(FeedState.feeding_plans, plan_card),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
                ),
            ),
            rx.el.button(
                rx.icon("plus", class_name="h-5 w-5 mr-2"),
                "Create Feeding Plan",
                on_click=lambda: FeedState.toggle_plan_dialog(True),
                class_name="mt-4 flex items-center bg-emerald-500 text-white px-5 py-3 rounded-xl font-semibold hover:bg-emerald-600 transition-all",
            ),
        ),
        "feed-plans",
    )


# ── Ration optimizer (cheapest balanced ration) ──────────────────────

def ration_item(item: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(item["name"], class_name="font-semibold text-sm text-stone-700"),
            rx.cond(
                item["in_stock"],
                rx.el.span(
                    "✓ in stock",
                    class_name="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 font-bold ml-2",
                ),
                None,
            ),
            class_name="flex items-center",
        ),
        rx.el.span(
            f"{item['qty']} {item['unit']} · ₹{item['cost']:.0f}",
            class_name="text-xs text-stone-500",
        ),
        class_name="flex items-center justify-between bg-stone-50 p-3 rounded-lg",
    )


def ration_optimizer_panel() -> rx.Component:
    return section(
        "Ration Optimizer",
        "Cheapest feed mix that covers the daily nutrient needs of a group.",
        "badge-rupee",
        rx.el.div(
            rx.el.label(
                "Animal Group",
                class_name="block text-sm font-medium text-stone-700 mb-1",
            ),
            rx.el.select(
                rx.foreach(
                    PLAN_CATEGORIES,
                    lambda c: rx.el.option(c, value=c),
                ),
                value=FeedState.ration_category,
                on_change=FeedState.set_ration_category,
                class_name="w-full px-3 py-2 border rounded-md bg-white",
            ),
            rx.cond(
                FeedState.feed_types.length() == 0,
                rx.el.p(
                    "Add feed types first.",
                    class_name="text-sm text-stone-500 text-center py-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.foreach(FeedState.cheapest_ration_items, ration_item),
                        class_name="space-y-2 mt-4",
                    ),
                    rx.el.div(
                        rx.el.span(
                            "Est. cost / day",
                            class_name="text-sm text-stone-500",
                        ),
                        rx.el.span(
                            f"₹{FeedState.cheapest_ration['total_cost']:,.0f}",
                            class_name="text-lg font-extrabold text-stone-800",
                        ),
                        class_name="flex items-center justify-between mt-4 pt-3 border-t border-stone-200",
                    ),
                    rx.el.p(
                        "Estimate based on nutrient density. Confirm with your veterinarian before changing rations.",
                        class_name="text-xs text-stone-400 mt-2",
                    ),
                ),
            ),
        ),
        "feed-ration",
    )


# ── Feed simulator ("what if…?") ─────────────────────────────────────

def sim_stat(label: str, value, sub: str) -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-xs text-stone-500"),
        rx.el.p(value, class_name="text-xl font-extrabold text-stone-800"),
        rx.el.p(sub, class_name="text-xs text-stone-400"),
        class_name="bg-stone-50 p-3 rounded-lg",
    )


def feed_simulator_panel() -> rx.Component:
    return section(
        "Feed Simulator",
        "\"What if I change a feed by X%?\" — see the estimated milk, cost and profit effect.",
        "flask-conical",
        rx.el.div(
            rx.el.label(
                "Feed", class_name="block text-sm font-medium text-stone-700 mb-1"
            ),
            rx.el.select(
                rx.foreach(
                    FeedState.feed_type_options,
                    lambda opt: rx.el.option(opt["label"], value=opt["id"]),
                ),
                value=FeedState.sim_feed_type_id,
                on_change=FeedState.set_sim_feed_type_id,
                class_name="w-full px-3 py-2 border rounded-md bg-white",
            ),
            rx.el.label(
                "Animal", class_name="block text-sm font-medium text-stone-700 mb-1 mt-4"
            ),
            rx.el.select(
                rx.foreach(
                    FeedState.sim_animal_options,
                    lambda a: rx.el.option(a["label"], value=a["id"]),
                ),
                value=FeedState.sim_animal_id,
                on_change=FeedState.set_sim_animal_id,
                class_name="w-full px-3 py-2 border rounded-md bg-white",
            ),
            rx.el.label(
                "Change (%)",
                class_name="block text-sm font-medium text-stone-700 mb-2 mt-4",
            ),
            rx.el.div(
                rx.foreach(
                    SIM_CHANGE_OPTIONS,
                    lambda v: rx.el.button(
                        v,
                        on_click=lambda: FeedState.set_sim_change(v),
                        class_name=rx.cond(
                            FeedState.sim_change_str == v,
                            "px-4 py-2 rounded-lg bg-emerald-500 text-white font-bold text-sm",
                            "px-4 py-2 rounded-lg bg-stone-100 text-stone-700 font-bold text-sm hover:bg-stone-200 transition-all",
                        ),
                    ),
                ),
                class_name="flex flex-wrap gap-2",
            ),
            rx.cond(
                FeedState.sim_feed_type_id != "",
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                FeedState.simulation_results["feed_name"],
                                class_name="font-bold text-stone-800",
                            ),
                            rx.el.p(
                                f"{FeedState.simulation_results['current_qty']} → {FeedState.simulation_results['new_qty']} {FeedState.simulation_results['unit']} / day",
                                class_name="text-xs text-stone-500",
                            ),
                            class_name="flex-1",
                        ),
                        rx.cond(
                            FeedState.simulation_results["verdict"] == "Profitable",
                            rx.el.span(
                                "💰 Profitable",
                                class_name="px-2 py-1 rounded-full bg-emerald-50 text-emerald-600 text-xs font-bold",
                            ),
                            rx.cond(
                                FeedState.simulation_results["verdict"] == "Not profitable",
                                rx.el.span(
                                    "⚠️ Not profitable",
                                    class_name="px-2 py-1 rounded-full bg-red-50 text-red-600 text-xs font-bold",
                                ),
                                rx.el.span(
                                    "⚖️ Break-even",
                                    class_name="px-2 py-1 rounded-full bg-stone-100 text-stone-500 text-xs font-bold",
                                ),
                            ),
                        ),
                        class_name="flex items-center gap-3",
                    ),
                    rx.el.div(
                        sim_stat(
                            "Milk change",
                            f"{FeedState.simulation_results['milk_gain']:+.1f} L/day",
                            f"currently {FeedState.simulation_results['current_milk']} L/day",
                        ),
                        sim_stat(
                            "Feed cost",
                            f"{FeedState.simulation_results['delta_cost']:+.0f} ₹/day",
                            "estimated change",
                        ),
                        sim_stat(
                            "Profit",
                            f"{FeedState.simulation_results['profit_change']:+.0f} ₹/day",
                            f"milk @ ₹{MILK_PRICE_PER_LITER:.0f}/L",
                        ),
                        class_name="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4",
                    ),
                    rx.el.p(
                        "Rough rule: +1 kg concentrate ≈ +0.8 L milk/day; +1 kg fodder ≈ +0.3 L/day. Estimate only.",
                        class_name="text-xs text-stone-400 mt-3",
                    ),
                    class_name="mt-5 bg-stone-50 rounded-xl p-4",
                ),
                rx.el.p(
                    "Pick a feed to see the estimate.",
                    class_name="text-sm text-stone-500 text-center py-6",
                ),
            ),
        ),
        "feed-simulator",
    )


# ── Analytics (spec: Feed Consumption + Feed Cost Analysis) ──────────

def stat_tile(icon: str, label: str, value, sub: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-5 w-5 text-emerald-500"),
        rx.el.p(label, class_name="text-xs text-stone-500 mt-2"),
        rx.el.p(value, class_name="text-2xl font-extrabold text-stone-800"),
        rx.el.p(sub, class_name="text-xs text-stone-400"),
        class_name="bg-stone-50 p-4 rounded-xl",
    )


def analytics_stats_panel() -> rx.Component:
    return section(
        "Consumption & Cost",
        "Today, weekly and monthly feed use at a glance.",
        "bar-chart-3",
        rx.el.div(
            rx.el.div(
                stat_tile(
                    "sunrise",
                    "Today",
                    f"{FeedState.daily_consumption_kg} kg",
                    "kg consumed",
                ),
                stat_tile(
                    "calendar-days",
                    "This Week",
                    f"{FeedState.weekly_consumption_kg} kg",
                    "kg consumed",
                ),
                stat_tile(
                    "calendar-range",
                    "This Month",
                    f"{FeedState.monthly_consumption_kg} kg",
                    "kg consumed",
                ),
                stat_tile(
                    "badge-rupee",
                    "Monthly Feed Cost",
                    f"₹{FeedState.monthly_feed_cost:,.0f}",
                    "consumption + purchases",
                ),
                stat_tile(
                    "droplets",
                    "Feed Cost / Liter",
                    f"₹{FeedState.feed_cost_per_liter:.2f}",
                    "per liter of milk",
                ),
                class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4",
            ),
        ),
        "feed-stats",
    )


def feed_trends_panel() -> rx.Component:
    return section(
        "Trends & Breakdown",
        "Feed cost trend and consumption by feed type.",
        "trending-up",
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Feed Cost Trend (6 months)",
                    class_name="text-sm font-semibold text-stone-600 mb-2",
                ),
                rx.recharts.area_chart(
                    rx.recharts.cartesian_grid(
                        vertical=False, stroke_dasharray="3 3"
                    ),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.x_axis(data_key="month", class_name="text-xs"),
                    rx.recharts.y_axis(class_name="text-xs"),
                    rx.recharts.area(
                        data_key="cost",
                        stroke="#10b981",
                        fill="#a7f3d0",
                        type_="monotone",
                    ),
                    data=FeedState.feed_cost_trend,
                    height=220,
                ),
                class_name="bg-stone-50 rounded-xl p-4 mt-4",
            ),
            rx.el.div(
                rx.el.p(
                    "Consumption by Feed (30 days)",
                    class_name="text-sm font-semibold text-stone-600 mb-2 mt-6",
                ),
                rx.el.div(
                    rx.foreach(
                        FeedState.consumption_by_feed,
                        lambda item: rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    item["name"],
                                    class_name="text-sm font-medium text-stone-700 truncate",
                                ),
                                rx.el.span(
                                    f"{item['qty']} kg · ₹{item['cost']:,.0f}",
                                    class_name="text-xs text-stone-500",
                                ),
                                class_name="flex items-center justify-between mb-1",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name="h-3 rounded-full bg-emerald-500 transition-all",
                                    style={"width": item["pct"].to_string() + "%"},
                                ),
                                class_name="w-full h-3 bg-stone-100 rounded-full overflow-hidden",
                            ),
                            class_name="mb-3",
                        ),
                    ),
                    class_name="mt-2",
                ),
                class_name="bg-stone-50 rounded-xl p-4 mt-4",
            ),
        ),
        "feed-trends",
    )


# ── Milk vs Feed (spec: core feature) ────────────────────────────────

def milk_feed_chart() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            "Milk vs Feed per Animal (L/day vs kg/day · 7-day averages)",
            class_name="text-sm font-semibold text-stone-600 mb-2",
        ),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.x_axis(data_key="name", class_name="text-xs"),
            rx.recharts.y_axis(class_name="text-xs"),
            rx.recharts.bar(
                data_key="milk",
                fill="#3b82f6",
                radius=[4, 4, 0, 0],
            ),
            rx.recharts.bar(
                data_key="feed",
                fill="#f59e0b",
                radius=[4, 4, 0, 0],
            ),
            data=FeedState.milk_feed_chart_data,
            height=230,
        ),
        class_name="bg-stone-50 rounded-xl p-4 mb-4",
    )


def insight_card(insight: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.span(insight["icon"], class_name=f"text-xl {insight['color']}"),
        rx.el.p(insight["text"], class_name="text-sm text-stone-700"),
        class_name="flex items-start gap-3 bg-stone-50 p-4 rounded-xl",
    )


def milk_feed_panel() -> rx.Component:
    return section(
        "Milk vs Feed Analysis",
        "See which feeding decisions are actually improving milk output.",
        "git-compare",
        rx.el.div(
            milk_feed_chart(),
            rx.cond(
            FeedState.milk_feed_insights.length() == 0,
            rx.el.p(
                "Record milk production and feeding for at least a week to unlock insights.",
                class_name="text-sm text-stone-500 text-center py-8 bg-stone-50 rounded-xl",
            ),
            rx.el.div(
                rx.foreach(FeedState.milk_feed_insights, insight_card),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-3",
            ),
        ),
        ),
        "feed-milkfeed",
    )


# ── Feed conversion efficiency (spec) ────────────────────────────────

def efficiency_score_chart() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            "Efficiency Score (0–100)",
            class_name="text-sm font-semibold text-stone-600 mb-2",
        ),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.x_axis(data_key="name", class_name="text-xs"),
            rx.recharts.y_axis(domain=[0, 100], class_name="text-xs"),
            rx.recharts.bar(
                data_key="score",
                fill="#8b5cf6",
                radius=[4, 4, 0, 0],
            ),
            data=FeedState.efficiency_chart_data,
            height=200,
        ),
        class_name="bg-stone-50 rounded-xl p-4 mb-4",
    )


def rank_badge(rank: rx.Var[str]) -> rx.Component:
    return rx.cond(
        rank == "Excellent",
        rx.el.span(
            "Excellent", class_name="px-2 py-1 rounded-full bg-emerald-50 text-emerald-600 text-xs font-bold"
        ),
        rx.cond(
            rank == "Good",
            rx.el.span(
                "Good", class_name="px-2 py-1 rounded-full bg-blue-50 text-blue-600 text-xs font-bold"
            ),
            rx.cond(
                rank == "Average",
                rx.el.span(
                    "Average", class_name="px-2 py-1 rounded-full bg-amber-50 text-amber-600 text-xs font-bold"
                ),
                rx.el.span(
                    "Needs Attention",
                    class_name="px-2 py-1 rounded-full bg-red-50 text-red-600 text-xs font-bold",
                ),
            ),
        ),
    )


def efficiency_row(row: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.image(
            src=row["image_url"],
            class_name="w-10 h-10 rounded-full object-cover border border-stone-200",
        ),
        rx.el.div(
            rx.el.p(row["name"], class_name="font-semibold text-stone-800 text-sm"),
            rx.el.p(
                f"{row['milk_per_kg']} L/kg · ₹{row['milk_per_rupee']} milk per ₹ feed",
                class_name="text-xs text-stone-500",
            ),
            class_name="flex-1 min-w-0",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    class_name="h-2 rounded-full bg-emerald-500",
                    style={"width": row["score"].to_string() + "%"},
                ),
                class_name="w-20 h-2 bg-stone-100 rounded-full overflow-hidden",
            ),
            rx.el.span(
                f"{row['score']}",
                class_name="text-xs font-bold text-stone-700 ml-2",
            ),
            class_name="flex items-center gap-2",
        ),
        rank_badge(row["rank"]),
        class_name="flex items-center gap-3 p-3 rounded-xl bg-stone-50",
    )


def efficiency_panel() -> rx.Component:
    return section(
        "Feed Conversion Efficiency",
        "Milk per kg of feed and per ₹ spent — animals ranked best to worst.",
        "gauge",
        rx.el.div(
            efficiency_score_chart(),
            rx.cond(
            FeedState.efficiency_ranks.length() == 0,
            rx.el.p(
                "Efficiency ranking needs both feeding and milk records.",
                class_name="text-sm text-stone-500 text-center py-8 bg-stone-50 rounded-xl",
            ),
            rx.el.div(
                rx.foreach(FeedState.efficiency_ranks, efficiency_row),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-3",
            ),
        ),
        ),
        "feed-efficiency",
    )


# ── Purchase planner (spec) ──────────────────────────────────────────

def suggestion_card(s: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.icon("shopping-cart", class_name="h-5 w-5 text-blue-500"),
        rx.el.p(s["text"], class_name="text-sm text-stone-700 flex-1"),
        rx.el.span(
            f"Buy {s['buy_qty']} {s['unit']}",
            class_name="text-xs font-bold px-3 py-1 rounded-full bg-blue-50 text-blue-600 flex-shrink-0",
        ),
        class_name="flex items-center gap-3 bg-stone-50 p-4 rounded-xl",
    )


def purchase_planner_panel() -> rx.Component:
    return section(
        "Feed Purchase Planner",
        "Know what to buy and when — based on stock left and consumption rate.",
        "shopping-cart",
        rx.cond(
            FeedState.purchase_suggestions.length() == 0,
            rx.el.p(
                "Record a few days of feeding to get purchase suggestions.",
                class_name="text-sm text-stone-500 text-center py-8 bg-stone-50 rounded-xl",
            ),
            rx.el.div(
                rx.foreach(FeedState.purchase_suggestions, suggestion_card),
                class_name="space-y-3",
            ),
        ),
        "feed-planner",
    )


# ── Smart alerts (spec) ──────────────────────────────────────────────

def alert_card(alert: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(alert["icon"], class_name="text-xl"),
            class_name=f"w-10 h-10 rounded-xl flex items-center justify-center {alert['color']}",
        ),
        rx.el.div(
            rx.el.p(alert["title"], class_name="font-semibold text-stone-800 text-sm"),
            rx.el.p(alert["text"], class_name="text-xs text-stone-500"),
            class_name="flex-1",
        ),
        class_name="flex items-center gap-3 bg-stone-50 p-4 rounded-xl",
    )


def smart_alerts_panel() -> rx.Component:
    return section(
        "Smart Alerts",
        "Low stock, expiring feed, consumption spikes — flagged automatically.",
        "bell-ring",
        rx.cond(
            FeedState.smart_alerts.length() == 0,
            rx.el.div(
                rx.icon("shield-check", class_name="h-8 w-8 text-emerald-400 mx-auto"),
                rx.el.p(
                    "All clear! No feed alerts right now.",
                    class_name="text-sm text-stone-500 text-center mt-2",
                ),
                class_name="py-8 bg-stone-50 rounded-xl",
            ),
            rx.el.div(
                rx.foreach(FeedState.smart_alerts, alert_card),
                class_name="space-y-3",
            ),
        ),
        "feed-alerts",
    )


# ── AI Nutrition Advisor (spec) ──────────────────────────────────────

def advisor_card(rec: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(rec["icon"], class_name="text-xl"),
            rx.el.p(rec["title"], class_name="font-bold text-sm"),
            class_name=f"flex items-center gap-2 px-4 py-3 rounded-t-xl border-b {rec['color']}",
        ),
        rx.el.p(rec["action"], class_name="text-sm text-stone-700 p-4"),
        class_name="bg-white rounded-xl border border-stone-200 overflow-hidden",
    )


def feed_advisor_panel() -> rx.Component:
    return section(
        "AI Nutrition Advisor",
        "Personalized feeding advice per animal — with a clear action for each.",
        "brain-circuit",
        rx.cond(
            FeedState.ai_recommendations.length() == 0,
            rx.el.p(
                "Record milk and feeding for a few days and the advisor will suggest improvements.",
                class_name="text-sm text-stone-500 text-center py-8 bg-stone-50 rounded-xl",
            ),
            rx.el.div(
                rx.foreach(FeedState.ai_recommendations, advisor_card),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
            ),
        ),
        "feed-advisor",
    )


# ── Feed reports (spec: Reports) ─────────────────────────────────────

REPORTS = [
    ("daily", "Daily Feed Report", "Today's feeding per animal with totals."),
    ("monthly_cost", "Monthly Feed Cost", "Feed spend, cost per liter, per-feed breakdown."),
    ("milk_feed", "Milk vs Feed Report", "Milk output vs feed intake per animal."),
    ("purchase", "Feed Purchase Report", "Stock, days remaining, and next purchase plan."),
    ("waste", "Feed Waste Report", "Animals eating more than they produce (potential waste)."),
    ("nutrition", "Animal Nutrition Report", "Per-animal intake, cost, and advisor recommendations."),
]


def report_card(report: rx.Var[dict]) -> rx.Component:
    return rx.el.div(
        rx.el.p(report[1], class_name="font-bold text-stone-800"),
        rx.el.p(report[2], class_name="text-xs text-stone-500 mt-1"),
        rx.el.button(
            rx.icon("download", class_name="h-4 w-4 mr-1"),
            "PDF",
            on_click=lambda: FeedState.generate_feed_report(report[0]),
            class_name="mt-3 flex items-center text-xs font-bold px-3 py-1.5 rounded-lg bg-emerald-500 text-white hover:bg-emerald-600",
        ),
        class_name="bg-stone-50 p-4 rounded-xl border border-stone-100",
    )


def feed_reports_panel() -> rx.Component:
    return section(
        "Feed Reports",
        "One-tap PDF reports you can print or share.",
        "file-text",
        rx.el.div(
            rx.foreach(REPORTS, report_card),
            class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4",
        ),
        "feed-reports",
    )

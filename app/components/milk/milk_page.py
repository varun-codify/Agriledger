"""Milk & Society Bills page.

Records milk deliveries from the society's bill slip (Aavin, Hatsun, etc.),
with optional OCR scanning so the farmer spends seconds on data entry.
"""

import reflex as rx

from app.components.layout import dashboard_layout
from app.states.cattle_state import CattleState
from app.states.milk_state import MilkState


def stat_card(
    title: str, icon: str, value: rx.Var, sub: str, color: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-5 w-5"),
            class_name=f"p-3 rounded-xl {color}",
        ),
        rx.el.p(title, class_name="text-xs text-stone-500 mt-3"),
        rx.el.p(value, class_name="text-2xl font-bold text-stone-800"),
        rx.el.p(sub, class_name="text-xs text-stone-400"),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def summary_cards() -> rx.Component:
    return rx.el.div(
        stat_card(
            "Litres Supplied (Month)",
            "droplets",
            MilkState.month_litres.to_string(),
            "across all societies",
            "text-sky-600 bg-sky-50",
        ),
        stat_card(
            "Milk Income (Month)",
            "indian-rupee",
            "₹" + MilkState.month_income.to_string(),
            "from society bills",
            "text-emerald-600 bg-emerald-50",
        ),
        stat_card(
            "Avg Fat % (Month)",
            "beef",
            MilkState.avg_fat_month.to_string(),
            "target 3.5–4.5%",
            "text-orange-600 bg-orange-50",
        ),
        stat_card(
            "Avg SNF % (Month)",
            "test-tube",
            MilkState.avg_snf_month.to_string(),
            "target 8.0–9.0%",
            "text-blue-600 bg-blue-50",
        ),
        stat_card(
            "Pending Payment",
            "hourglass",
            "₹" + MilkState.pending_amount.to_string(),
            "bills not yet paid",
            "text-amber-600 bg-amber-50",
        ),
        class_name="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-6",
    )


def scan_card() -> rx.Component:
    """OCR dropzone for the society bill photo."""
    return rx.el.div(
        rx.el.h3(
            "📷 Scan Society Bill",
            class_name="text-lg font-semibold text-stone-800 mb-1",
        ),
        rx.el.p(
            "Take a photo of the Aavin / Hatsun bill slip — fat %, SNF %, "
            "litres, rate and amount are filled in for you.",
            class_name="text-sm text-stone-500 mb-4",
        ),
        rx.upload(
            rx.el.div(
                rx.cond(
                    MilkState.scanning,
                    rx.el.div(
                        rx.icon(
                            "loader-circle",
                            class_name="h-10 w-10 text-emerald-500 animate-spin mx-auto",
                        ),
                        rx.el.p(
                            "Reading the bill…",
                            class_name="text-sm font-medium text-stone-600 mt-2",
                        ),
                        class_name="text-center",
                    ),
                    rx.el.div(
                        rx.icon(
                            "scan-line",
                            class_name="h-10 w-10 text-emerald-500 mx-auto",
                        ),
                        rx.el.p(
                            "Click to select or drag the bill photo here",
                            class_name="text-sm font-medium text-stone-600 mt-2",
                        ),
                        rx.el.p(
                            "JPG / PNG — the image never leaves your device's "
                            "internet connection except to Gemini",
                            class_name="text-xs text-stone-400 mt-1",
                        ),
                        class_name="text-center",
                    ),
                ),
                class_name="p-8",
            ),
            id="milk-bill-upload",
            multiple=False,
            max_files=1,
            accept={"image/*": [".jpg", ".jpeg", ".png", ".webp"]},
            on_drop=MilkState.handle_bill_upload,
            class_name="w-full border-2 border-dashed border-emerald-300 rounded-2xl "
            "bg-emerald-50/50 hover:border-emerald-400 hover:bg-emerald-50 transition",
        ),
        rx.cond(
            MilkState.scan_message != "",
            rx.el.div(
                rx.icon(
                    "circle-check",
                    class_name="h-4 w-4 mr-2 flex-shrink-0 text-emerald-600",
                ),
                MilkState.scan_message,
                class_name="flex items-start text-sm text-emerald-700 bg-emerald-50 "
                "border border-emerald-200 p-3 rounded-lg mt-4",
            ),
            None,
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def form_field(
    label: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    input_type: str = "number",
    placeholder: str = "",
    hint: str = "",
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label, class_name="block text-sm font-medium text-stone-700 mb-1"
        ),
        rx.el.input(
            type=input_type,
            value=value,
            on_change=on_change,
            placeholder=placeholder,
            class_name="w-full px-3 py-2 rounded-lg border border-stone-300 "
            "focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition",
        ),
        rx.cond(
            hint != "",
            rx.el.p(hint, class_name="text-xs text-stone-400 mt-0.5"),
            None,
        ),
    )


def milk_entry_form() -> rx.Component:
    """The bill-slip entry form."""
    return rx.el.div(
        rx.el.h3(
            "Enter Bill Slip",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.el.div(
            # Society + date
            rx.el.div(
                rx.el.label(
                    "Milk Society",
                    class_name="block text-sm font-medium text-stone-700 mb-1",
                ),
                rx.el.select(
                    rx.foreach(
                        MilkState.societies,
                        lambda s: rx.el.option(s, value=s),
                    ),
                    value=MilkState.society,
                    on_change=MilkState.set_society,
                    class_name="w-full px-3 py-2 rounded-lg border border-stone-300 "
                    "focus:ring-2 focus:ring-emerald-500 transition",
                ),
            ),
            form_field("Date", MilkState.date, MilkState.set_date, "date"),
            form_field(
                "Litres",
                MilkState.liters.to_string(),
                MilkState.set_liters,
                placeholder="e.g., 12.5",
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-3",
        ),
        rx.el.div(
            form_field(
                "Fat %",
                MilkState.fat_percentage.to_string(),
                MilkState.set_fat_percentage,
                placeholder="e.g., 4.2",
            ),
            form_field(
                "SNF %",
                MilkState.snf_percentage.to_string(),
                MilkState.set_snf_percentage,
                placeholder="e.g., 8.5",
            ),
            form_field(
                "CLR (optional)",
                MilkState.clr.to_string(),
                MilkState.set_clr,
                placeholder="e.g., 30",
            ),
            class_name="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3",
        ),
        # Suggested rate from fat% slab table
        rx.cond(
            MilkState.suggested_rate > 0,
            rx.el.div(
                rx.icon("lightbulb", class_name="h-4 w-4 text-amber-500 mr-2"),
                rx.el.p(
                    "Rate for " + MilkState.fat_percentage.to_string() + "% fat: ₹"
                    + MilkState.suggested_rate.to_string() + "/L",
                    class_name="text-sm text-amber-700",
                ),
                rx.el.button(
                    "Use this rate",
                    on_click=MilkState.use_suggested_rate,
                    class_name="ml-3 px-3 py-1 rounded-md bg-amber-100 text-amber-700 "
                    "text-xs font-semibold hover:bg-amber-200 transition",
                ),
                class_name="flex items-center mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg",
            ),
            None,
        ),
        rx.el.div(
            form_field(
                "Rate per Litre (₹)",
                MilkState.rate_per_liter.to_string(),
                MilkState.set_rate_per_liter,
                placeholder="e.g., 40",
            ),
            form_field(
                "Amount from Bill (₹)",
                MilkState.amount.to_string(),
                MilkState.set_amount,
                placeholder="e.g., 500",
            ),
            form_field(
                "Bill Number",
                MilkState.bill_number,
                MilkState.set_bill_number,
                input_type="text",
                placeholder="optional",
            ),
            class_name="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-3",
        ),
        # Mismatch warning when bill amount ≠ litres × rate
        rx.cond(
            MilkState.amount_mismatch,
            rx.el.div(
                rx.icon("triangle-alert", class_name="h-4 w-4 mr-2 flex-shrink-0"),
                rx.el.p(
                    "Bill amount (₹" + MilkState.amount.to_string()
                    + ") doesn't match " + MilkState.liters.to_string()
                    + " L × ₹" + MilkState.rate_per_liter.to_string()
                    + " = ₹" + MilkState.expected_amount.to_string()
                    + ". Double-check the slip before saving.",
                    class_name="text-sm text-red-600",
                ),
                class_name="flex items-start p-3 bg-red-50 border border-red-200 rounded-lg mt-3",
            ),
            None,
        ),
        rx.el.div(
            rx.el.label(
                "Payment Status",
                class_name="block text-sm font-medium text-stone-700 mb-1",
            ),
            rx.el.select(
                rx.el.option("Pending (not paid yet)", value="pending"),
                rx.el.option("Paid", value="paid"),
                value=MilkState.payment_status,
                on_change=MilkState.set_payment_status,
                class_name="w-full px-3 py-2 rounded-lg border border-stone-300 "
                "focus:ring-2 focus:ring-emerald-500 transition",
            ),
        ),
        rx.el.div(
            rx.el.label(
                "Animal (optional)",
                class_name="block text-sm font-medium text-stone-700 mb-1",
            ),
            rx.el.select(
                rx.el.option("— No animal —", value=""),
                rx.foreach(
                    CattleState.breedable_females,
                    lambda c: rx.el.option(c["name"], value=c["id"]),
                ),
                value=MilkState.animal_id,
                on_change=MilkState.set_animal_id,
                class_name="w-full px-3 py-2 rounded-lg border border-stone-300 "
                "focus:ring-2 focus:ring-emerald-500 transition",
            ),
        ),
        form_field(
            "Notes (optional)",
            MilkState.notes,
            MilkState.set_notes,
            input_type="text",
            placeholder="e.g., morning delivery",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("check", class_name="h-4 w-4 mr-2"),
                "Save Bill",
                on_click=MilkState.add_bill,
                class_name="flex items-center px-5 py-2.5 rounded-lg bg-emerald-600 "
                "text-white font-semibold hover:bg-emerald-700 transition shadow-sm",
            ),
            rx.el.button(
                "Clear",
                on_click=MilkState.reset_form,
                class_name="px-5 py-2.5 rounded-lg bg-stone-100 text-stone-600 "
                "font-semibold hover:bg-stone-200 transition",
            ),
            class_name="flex gap-3 mt-4",
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
    )


def rate_checker() -> rx.Component:
    """Editable fat%-slab rate table per society."""
    return rx.el.div(
        rx.el.h3(
            "Rate Checker",
            class_name="text-lg font-semibold text-stone-800 mb-1",
        ),
        rx.el.p(
            "Societies price milk by fat %. Add the slab rates from your "
            "society's rate card — the entry form then suggests the rate for "
            "each fat reading and flags bill mismatches.",
            class_name="text-sm text-stone-500 mb-4",
        ),
        rx.el.div(
            rx.el.select(
                rx.foreach(
                    MilkState.societies,
                    lambda s: rx.el.option(s, value=s),
                ),
                value=MilkState.rate_society,
                on_change=MilkState.set_rate_society,
                class_name="w-full px-3 py-2 rounded-lg border border-stone-300 "
                "focus:ring-2 focus:ring-emerald-500 transition",
            ),
            rx.el.button(
                "Load",
                on_click=MilkState.load_rate_table,
                class_name="px-4 py-2 rounded-lg bg-stone-100 text-stone-600 "
                "text-sm font-semibold hover:bg-stone-200 transition",
            ),
            class_name="flex gap-2",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    "Fat % at least", class_name="text-xs text-stone-500 flex-1"
                ),
                rx.el.span(
                    "Rate (₹/L)", class_name="text-xs text-stone-500 w-24 text-right"
                ),
                class_name="flex gap-2 px-1 mb-1",
            ),
            rx.cond(
                MilkState.rate_slabs.length() == 0,
                rx.el.p(
                    "No slabs yet. Add the society's rate card below.",
                    class_name="text-xs text-stone-400 py-2",
                ),
                rx.el.div(
                    rx.foreach(
                        MilkState.rate_slabs,
                        lambda slab, i: rx.el.div(
                            rx.el.input(
                                type="number",
                                value=slab["fat_min"].to_string(),
                                on_change=lambda v: MilkState.set_slab_fat(i, v),
                                class_name="flex-1 px-2 py-1.5 rounded-md border "
                                "border-stone-300 focus:ring-2 focus:ring-emerald-500",
                            ),
                            rx.el.input(
                                type="number",
                                value=slab["rate"].to_string(),
                                on_change=lambda v: MilkState.set_slab_rate(i, v),
                                class_name="w-24 px-2 py-1.5 rounded-md border "
                                "border-stone-300 focus:ring-2 focus:ring-emerald-500",
                            ),
                            rx.el.button(
                                rx.icon("trash-2", class_name="h-4 w-4"),
                                on_click=lambda: MilkState.remove_slab(i),
                                class_name="p-2 rounded-md text-red-500 hover:bg-red-50 transition",
                            ),
                            class_name="flex items-center gap-2 mb-2",
                        ),
                    ),
                    class_name="",
                ),
            ),
            rx.el.button(
                rx.icon("plus", class_name="h-4 w-4 mr-1"),
                "Add Slab",
                on_click=MilkState.add_slab,
                class_name="flex items-center px-3 py-1.5 rounded-md bg-stone-100 "
                "text-stone-600 text-sm font-semibold hover:bg-stone-200 transition",
            ),
            class_name="mt-4",
        ),
        rx.el.button(
            "Save Rate Table",
            on_click=MilkState.save_rate_table,
            class_name="w-full mt-4 px-4 py-2.5 rounded-lg bg-emerald-600 text-white "
            "font-semibold hover:bg-emerald-700 transition",
        ),
        rx.cond(
            MilkState.rate_saved,
            rx.el.p(
                "Saved ✓", class_name="text-xs text-emerald-600 mt-2 text-center"
            ),
            None,
        ),
        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 h-full",
    )


def society_performance() -> rx.Component:
    """Per-society month-to-date cards."""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Society Performance",
                class_name="text-lg font-semibold text-stone-800",
            ),
            rx.el.p(
                "This month", class_name="text-sm text-stone-400"
            ),
            class_name="flex items-end justify-between mb-4",
        ),
        rx.cond(
            MilkState.society_stats.length() == 0,
            rx.el.p(
                "No bills recorded this month yet. Save your first society bill "
                "above to see the comparison.",
                class_name="text-sm text-stone-400 bg-white border border-stone-100 "
                "rounded-2xl p-6",
            ),
            rx.el.div(
                rx.foreach(
                    MilkState.society_stats,
                    lambda s: rx.el.div(
                        rx.el.div(
                            rx.icon("landmark", class_name="h-5 w-5 text-emerald-600"),
                            rx.el.p(
                                s["society"], class_name="font-semibold text-stone-800"
                            ),
                            rx.el.span(
                                s["bills"].to_string() + " bills",
                                class_name="text-xs px-2 py-0.5 rounded-full bg-stone-100 "
                                "text-stone-500",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.p("Litres", class_name="text-xs text-stone-400"),
                                rx.el.p(
                                    s["litres"].to_string(),
                                    class_name="text-xl font-bold text-stone-800",
                                ),
                            ),
                            rx.el.div(
                                rx.el.p("Income", class_name="text-xs text-stone-400"),
                                rx.el.p(
                                    "₹" + s["income"].to_string(),
                                    class_name="text-xl font-bold text-emerald-600",
                                ),
                            ),
                            rx.el.div(
                                rx.el.p("Avg Fat / SNF", class_name="text-xs text-stone-400"),
                                rx.el.p(
                                    s["avg_fat"].to_string() + " / " + s["avg_snf"].to_string(),
                                    class_name="text-xl font-bold text-stone-800",
                                ),
                            ),
                            rx.el.div(
                                rx.el.p("Pending", class_name="text-xs text-stone-400"),
                                rx.el.p(
                                    "₹" + s["pending"].to_string(),
                                    class_name="text-xl font-bold text-amber-600",
                                ),
                            ),
                            class_name="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4",
                        ),
                        class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100",
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6",
            ),
        ),
        class_name="mt-6",
    )


def bills_table() -> rx.Component:
    """History of recorded society bills with paid/pending + delete."""
    return rx.el.div(
        rx.el.h2(
            "Bill History", class_name="text-lg font-semibold text-stone-800 mb-4"
        ),
        rx.cond(
            MilkState.milk_sales.length() == 0,
            rx.el.p(
                "No milk bills recorded yet.",
                class_name="text-sm text-stone-400 bg-white border border-stone-100 "
                "rounded-2xl p-6",
            ),
            rx.el.div(
                rx.foreach(
                    MilkState.milk_sales,
                    lambda s: rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                s["date"], class_name="text-sm font-semibold text-stone-800"
                            ),
                            rx.el.p(
                                rx.cond(s.get("bill_number", ""), s.get("bill_number", ""), "—"),
                                class_name="text-xs text-stone-400",
                            ),
                        ),
                        rx.el.div(
                            rx.icon("landmark", class_name="h-4 w-4 text-stone-400"),
                            rx.el.span(
                                s.get("buyer", "—"),
                                class_name="text-sm font-medium text-stone-700",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        rx.el.div(
                            rx.el.p(
                                s["liters"].to_string() + " L",
                                class_name="text-sm font-bold text-stone-800",
                            ),
                            rx.el.p(
                                "Fat " + s["fat_percentage"].to_string() + "% · SNF "
                                + s["snf_percentage"].to_string() + "%",
                                class_name="text-xs text-stone-400",
                            ),
                        ),
                        rx.el.div(
                            rx.el.p(
                                "₹" + s["total_price"].to_string(),
                                class_name="text-sm font-bold text-emerald-600",
                            ),
                            rx.el.p(
                                "@ ₹" + s["rate_per_liter"].to_string() + "/L",
                                class_name="text-xs text-stone-400",
                            ),
                        ),
                        rx.cond(
                            s.get("payment_status", "pending") == "paid",
                            rx.el.span(
                                "Paid",
                                class_name="px-2 py-1 rounded-full text-xs font-semibold "
                                "bg-emerald-100 text-emerald-700",
                            ),
                            rx.el.span(
                                "Pending",
                                class_name="px-2 py-1 rounded-full text-xs font-semibold "
                                "bg-amber-100 text-amber-700",
                            ),
                        ),
                        rx.el.div(
                            rx.cond(
                                s.get("payment_status", "pending") == "paid",
                                rx.el.button(
                                    "Mark Pending",
                                    on_click=lambda: MilkState.toggle_payment(s["id"]),
                                    class_name="px-3 py-1.5 rounded-md text-xs font-semibold "
                                    "bg-stone-100 text-stone-600 hover:bg-stone-200 transition",
                                ),
                                rx.el.button(
                                    "Mark Paid",
                                    on_click=lambda: MilkState.toggle_payment(s["id"]),
                                    class_name="px-3 py-1.5 rounded-md text-xs font-semibold "
                                    "bg-emerald-100 text-emerald-700 hover:bg-emerald-200 transition",
                                ),
                            ),
                            rx.cond(
                                MilkState.pending_delete_id == s["id"],
                                rx.el.button(
                                    "Confirm?",
                                    on_click=lambda: MilkState.delete_bill(s["id"]),
                                    class_name="px-3 py-1.5 rounded-md text-xs font-semibold "
                                    "bg-red-600 text-white hover:bg-red-700 transition",
                                ),
                                rx.el.button(
                                    rx.icon("trash-2", class_name="h-4 w-4"),
                                    on_click=lambda: MilkState.set_pending_delete_id(s["id"]),
                                    class_name="p-1.5 rounded-md text-red-400 hover:bg-red-50 "
                                    "hover:text-red-600 transition",
                                ),
                            ),
                            class_name="flex gap-2",
                        ),
                        class_name="grid grid-cols-2 md:grid-cols-6 items-center gap-4 "
                        "bg-white p-4 rounded-2xl shadow-sm border border-stone-100 mb-3",
                    ),
                ),
                class_name="",
            ),
        ),
        class_name="mt-6",
    )


def milk_page() -> rx.Component:
    """The full Milk & Society Bills page."""
    return dashboard_layout(
        rx.el.div(
            summary_cards(),
            rx.el.div(
                rx.el.div(
                    scan_card(),
                    rx.el.div(class_name="h-6"),
                    milk_entry_form(),
                    class_name="lg:col-span-2",
                ),
                rate_checker(),
                class_name="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6",
            ),
            society_performance(),
            bills_table(),
            class_name="max-w-7xl mx-auto",
        ),
        "Milk & Society Bills",
    )

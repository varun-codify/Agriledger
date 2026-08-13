import reflex as rx

from app.states.cattle_state import CattleState
from app.states.milk_state import DEFAULT_SOCIETIES
from app.states.transaction_state import TransactionState


def milk_field(
    label: str,
    placeholder: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    input_type: str = "text",
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-stone-700 mb-1"),
        rx.el.input(
            type=input_type,
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition",
        ),
    )


def step_8_milk() -> rx.Component:
    """Wizard step 8: Milk sale details with quality metrics and auto-total."""
    return rx.el.div(
        rx.el.h2(
            "Milk Sale Details",
            class_name="text-2xl font-bold text-stone-800 text-center mb-8",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Animal (optional)", class_name="block text-sm font-medium text-stone-700 mb-1"
                ),
                rx.el.select(
                    rx.el.option("— Select animal —", value=""),
                    rx.foreach(
                        CattleState.breedable_females,
                        lambda c: rx.el.option(c["name"], value=c["id"]),
                    ),
                    value=TransactionState.animal_id,
                    on_change=TransactionState.set_animal_id,
                    class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 transition",
                ),
            ),
            milk_field(
                "Litres",
                "e.g., 20",
                TransactionState.liters.to_string(),
                TransactionState.set_liters,
                input_type="number",
            ),
            milk_field(
                "Rate per Litre (₹)",
                "e.g., 40",
                TransactionState.rate_per_liter.to_string(),
                TransactionState.set_rate_per_liter,
                input_type="number",
            ),
            rx.el.div(
                milk_field(
                    "Fat %",
                    "e.g., 4.2",
                    TransactionState.fat_percentage.to_string(),
                    TransactionState.set_fat_percentage,
                    input_type="number",
                ),
                milk_field(
                    "SNF %",
                    "e.g., 8.5",
                    TransactionState.snf_percentage.to_string(),
                    TransactionState.set_snf_percentage,
                    input_type="number",
                ),
                milk_field(
                    "CLR (optional)",
                    "e.g., 30",
                    TransactionState.clr.to_string(),
                    TransactionState.set_clr,
                    input_type="number",
                ),
                class_name="grid grid-cols-1 sm:grid-cols-3 gap-4",
            ),
            milk_field(
                "Water Ratio (optional)",
                "e.g., 1.2",
                TransactionState.water_ratio.to_string(),
                TransactionState.set_water_ratio,
                input_type="number",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Milk Society",
                        class_name="block text-sm font-medium text-stone-700 mb-1",
                    ),
                    rx.el.select(
                        rx.foreach(
                            DEFAULT_SOCIETIES,
                            lambda s: rx.el.option(s, value=s),
                        ),
                        value=TransactionState.buyer,
                        on_change=TransactionState.set_buyer,
                        class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 transition",
                    ),
                ),
                milk_field(
                    "Bill Number",
                    "optional",
                    TransactionState.bill_number,
                    TransactionState.set_bill_number,
                ),
                class_name="grid grid-cols-1 sm:grid-cols-2 gap-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Payment Status",
                    class_name="block text-sm font-medium text-stone-700 mb-1",
                ),
                rx.el.select(
                    rx.el.option("Pending (not paid yet)", value="pending"),
                    rx.el.option("Paid", value="paid"),
                    value=TransactionState.payment_status,
                    on_change=TransactionState.set_payment_status,
                    class_name="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500 transition",
                ),
            ),
            milk_field(
                "Date",
                "",
                TransactionState.date,
                TransactionState.set_date,
                input_type="date",
            ),
            rx.el.div(
                rx.el.p("Total Price", class_name="text-sm text-stone-500"),
                rx.el.p(
                    "₹" + TransactionState.milk_total_price.to_string(),
                    class_name="text-3xl font-bold text-emerald-600",
                ),
                class_name="text-center bg-emerald-50 rounded-xl p-4",
            ),
            class_name="space-y-4 max-w-md mx-auto",
        ),
        class_name="w-full",
    )

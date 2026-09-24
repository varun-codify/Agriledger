import datetime
from collections import defaultdict
from typing import TypedDict

import reflex as rx

from app.services.scheduler_service import SchedulerService
from app.states.breeding_state import BreedingState
from app.states.cattle_state import CattleState
from app.states.crop_state import CropState, WEATHER_CODES
from app.states.transaction_state import TransactionState


class SummaryMetric(TypedDict):
    title: str
    icon: str
    value: str
    change: str
    change_type: str


class ExpenseData(TypedDict):
    name: str
    value: int
    fill: str


class MilkData(TypedDict):
    day: str
    liters: int


class WeatherHighlight(TypedDict):
    temp: str
    condition: str
    icon: str
    tip: str


class Reminder(TypedDict):
    task: str
    due: str
    icon: str


class ChartData(TypedDict):
    label: str
    value: float | int


# Fallback demo data, shown only while there is no real farm data yet.
_DEMO_SUMMARY_METRICS: list[SummaryMetric] = [
    {"title": "Total Income", "icon": "trending-up", "value": "₹0", "change": "", "change_type": "up"},
    {"title": "Total Expenses", "icon": "trending-down", "value": "₹0", "change": "", "change_type": "down"},
    {"title": "Net Profit", "icon": "indian-rupee", "value": "₹0", "change": "", "change_type": "up"},
    {"title": "Milk Supplied (Month)", "icon": "droplets", "value": "0 L", "change": "", "change_type": "up"},
    {"title": "Milk Income (Month)", "icon": "droplets", "value": "₹0", "change": "", "change_type": "up"},
    {"title": "Coconut Sales (Month)", "icon": "tree-palm", "value": "0", "change": "", "change_type": "up"},
]

_DEMO_EXPENSE_DATA: list[ExpenseData] = [
    {"name": "Feed", "value": 400, "fill": "#10b981"},
    {"name": "Medicine", "value": 300, "fill": "#f97316"},
    {"name": "Labor", "value": 300, "fill": "#06b6d4"},
    {"name": "Utilities", "value": 200, "fill": "#f59e0b"},
    {"name": "Other", "value": 278, "fill": "#8b5cf6"},
]

_DEMO_MILK_PRODUCTION_DATA: list[MilkData] = [
    {"day": "Mon", "liters": 180},
    {"day": "Tue", "liters": 210},
    {"day": "Wed", "liters": 200},
    {"day": "Thu", "liters": 225},
    {"day": "Fri", "liters": 205},
    {"day": "Sat", "liters": 230},
    {"day": "Sun", "liters": 215},
]

_DEMO_WEATHER_HIGHLIGHT: WeatherHighlight = {
    "temp": "28°C",
    "condition": "Sunny",
    "icon": "sun",
    "tip": "Perfect day for harvesting. Low humidity.",
}

_DEMO_REMINDERS: list[Reminder] = [
    {"task": "Add farm data to see smart reminders", "due": "", "icon": "bell"},
]

_EXPENSE_FILLS = [
    "#10b981",
    "#f97316",
    "#06b6d4",
    "#f59e0b",
    "#8b5cf6",
    "#ec4899",
    "#ef4444",
    "#64748b",
]


class DashboardState(rx.State):
    """Manages the state for the main dashboard (all data derived from real records)."""

    active_pie_slice_name: str = ""
    active_pie_slice_value: str = ""

    @staticmethod
    def _parse_date(value) -> datetime.date | None:
        """Parse an ISO date string defensively; None when malformed.

        One malformed date in the database must never take down a computed
        var (and with it the whole dashboard render).
        """
        try:
            return datetime.date.fromisoformat(str(value))
        except (TypeError, ValueError):
            return None
    # ── Computed metrics (real data, with demo fallbacks) ────────────────

    @rx.var
    async def summary_metrics(self) -> list[SummaryMetric]:
        ts = await self.get_state(TransactionState)
        income = sum(float(t["amount"]) for t in ts.transactions if t["type"] == "income")
        expense = sum(float(t["amount"]) for t in ts.transactions if t["type"] == "expense")
        net = income - expense
        today = datetime.date.today()
        milk_month_sales = [
            s
            for s in ts.milk_sales
            if (d := self._parse_date(s.get("date"))) is not None
            and d.month == today.month
            and d.year == today.year
        ]
        milk_litres_month = sum(float(s.get("liters", 0)) for s in milk_month_sales)
        milk_income_month = sum(float(s.get("total_price", 0)) for s in milk_month_sales)
        coconut_month = sum(
            1
            for s in ts.coconut_sales
            if (d := self._parse_date(s.get("date"))) is not None
            and d.month == today.month
            and d.year == today.year
        )
        return [
            {"title": "Total Income", "icon": "trending-up", "value": f"₹{income:,.0f}", "change": "", "change_type": "up"},
            {"title": "Total Expenses", "icon": "trending-down", "value": f"₹{expense:,.0f}", "change": "", "change_type": "down"},
            {"title": "Net Profit", "icon": "indian-rupee", "value": f"₹{net:,.0f}", "change": "", "change_type": "up" if net >= 0 else "down"},
            {"title": "Milk Supplied (Month)", "icon": "droplets", "value": f"{milk_litres_month:.0f} L", "change": "", "change_type": "up"},
            {"title": "Milk Income (Month)", "icon": "droplets", "value": f"₹{milk_income_month:,.0f}", "change": "", "change_type": "up"},
            {"title": "Coconut Sales (Month)", "icon": "tree-palm", "value": str(coconut_month), "change": "", "change_type": "up"},
        ]

    @rx.var
    async def total_expenses(self) -> float:
        ts = await self.get_state(TransactionState)
        total = sum(
            float(t["amount"]) for t in ts.transactions if t["type"] == "expense"
        )
        return total if total > 0 else sum(item["value"] for item in _DEMO_EXPENSE_DATA)

    @rx.var
    async def expense_data(self) -> list[ExpenseData]:
        ts = await self.get_state(TransactionState)
        totals: dict[str, float] = defaultdict(float)
        for tx in ts.transactions:
            if tx["type"] == "expense":
                totals[tx["category"]["name"]] += float(tx["amount"])
        if not totals:
            return _DEMO_EXPENSE_DATA
        top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:5]
        return [
            {"name": name, "value": round(value), "fill": _EXPENSE_FILLS[i % len(_EXPENSE_FILLS)]}
            for i, (name, value) in enumerate(top)
        ]

    @rx.var
    async def milk_production_data(self) -> list[MilkData]:
        ts = await self.get_state(TransactionState)
        if not ts.milk_sales:
            return _DEMO_MILK_PRODUCTION_DATA
        by_day: dict[str, float] = defaultdict(float)
        for sale in ts.milk_sales:
            by_day[sale["date"]] += float(sale.get("liters", 0))
        today = datetime.date.today()
        data = []
        for i in range(6, -1, -1):
            day = today - datetime.timedelta(days=i)
            data.append(
                {"day": day.strftime("%a"), "liters": round(by_day.get(day.isoformat(), 0))}
            )
        return data

    @rx.var
    async def weather_highlight(self) -> WeatherHighlight:
        cs = await self.get_state(CropState)
        if cs.weather_data and cs.weather_data.get("current"):
            current = cs.weather_data["current"]
            condition, icon = WEATHER_CODES.get(
                current.get("weather_code", 0), ("Unknown", "cloud-question")
            )
            return {
                "temp": f'{round(current.get("temperature_2m", 0))}°C',
                "condition": condition,
                "icon": icon,
                "tip": (
                    f'Humidity {current.get("relative_humidity_2m", 0)}% · '
                    f'Wind {round(current.get("wind_speed_10m", 0))} km/h'
                ),
            }
        return _DEMO_WEATHER_HIGHLIGHT

    @rx.var
    async def reminders(self) -> list[Reminder]:
        bs = await self.get_state(BreedingState)
        cs = await self.get_state(CattleState)
        alerts = await SchedulerService.generate_all_alerts(bs.breeding_cycles, cs.cattle_list)
        if not alerts:
            return _DEMO_REMINDERS
        icon_map = {
            "breeding_check": "clipboard-check",
            "calving_expected": "siren",
            "rebreeding": "refresh-ccw",
            "vaccination": "syringe",
            "vaccination_overdue": "syringe",
            "health": "stethoscope",
        }
        return [
            {
                "task": alert["message"],
                "due": alert.get("due_date", ""),
                "icon": icon_map.get(alert["type"], "bell"),
            }
            for alert in alerts[:6]
        ]

    # ── Derived dashboard vars (unchanged behavior) ──────────────────────

    @rx.var
    async def total_coconuts_sold_month(self) -> int:
        ts = await self.get_state(TransactionState)
        today = datetime.date.today()
        current_month_sales = [
            s
            for s in ts.coconut_sales
            if (d := self._parse_date(s.get("date"))) is not None
            and d.month == today.month
            and d.year == today.year
        ]
        return sum((s["coconut_count"] for s in current_month_sales))

    @rx.var
    async def coconut_revenue_month(self) -> float:
        ts = await self.get_state(TransactionState)
        today = datetime.date.today()
        current_month_sales = [
            s
            for s in ts.coconut_sales
            if (d := self._parse_date(s.get("date"))) is not None
            and d.month == today.month
            and d.year == today.year
        ]
        return sum((s["total_amount"] for s in current_month_sales))

    @rx.var
    async def avg_fat_percentage_week(self) -> float:
        ts = await self.get_state(TransactionState)
        last_week = datetime.date.today() - datetime.timedelta(days=7)
        recent_sales = [
            s
            for s in ts.milk_sales
            if (d := self._parse_date(s.get("date"))) is not None
            and d >= last_week
        ]
        if not recent_sales:
            return 0.0
        avg = sum((s["fat_percentage"] for s in recent_sales)) / len(recent_sales)
        return round(avg, 2)

    @rx.var
    async def avg_snf_percentage_week(self) -> float:
        ts = await self.get_state(TransactionState)
        last_week = datetime.date.today() - datetime.timedelta(days=7)
        recent_sales = [
            s
            for s in ts.milk_sales
            if (d := self._parse_date(s.get("date"))) is not None
            and d >= last_week
        ]
        if not recent_sales:
            return 0.0
        avg = sum((s["snf_percentage"] for s in recent_sales)) / len(recent_sales)
        return round(avg, 2)

    @rx.var
    async def coconut_sales_data(self) -> list[dict]:
        ts = await self.get_state(TransactionState)
        sales_by_month = defaultdict(lambda: {"volume": 0, "revenue": 0})
        today = datetime.date.today()
        for sale in ts.coconut_sales:
            sale_date = self._parse_date(sale.get("date"))
            if sale_date is None or (
                (today.year - sale_date.year) * 12
                + (today.month - sale_date.month)
            ) >= 6:
                continue
                month_key = sale_date.strftime("%b %Y")
                sales_by_month[month_key]["volume"] += sale["coconut_count"]
                sales_by_month[month_key]["revenue"] += sale["total_amount"]
        data = []
        for i in range(5, -1, -1):
            month = today - datetime.timedelta(days=30 * i)
            month_key = month.strftime("%b %Y")
            data.append(
                {
                    "month": month.strftime("%b"),
                    "volume": sales_by_month[month_key]["volume"],
                    "revenue": sales_by_month[month_key]["revenue"],
                }
            )
        return data

    @rx.var
    async def milk_fat_trend_data(self) -> list[dict]:
        ts = await self.get_state(TransactionState)
        last_30_days = datetime.date.today() - datetime.timedelta(days=30)
        recent_sales = sorted(
            [
                s
                for s in ts.milk_sales
                if (d := self._parse_date(s.get("date"))) is not None
                and d >= last_30_days
            ],
            key=lambda s: s["date"],
        )
        return [
            {
                "day": datetime.date.fromisoformat(s["date"]).strftime("%b %d"),
                "fat_percentage": s["fat_percentage"],
            }
            for s in recent_sales
        ]

    @rx.var
    async def milk_snf_trend_data(self) -> list[dict]:
        ts = await self.get_state(TransactionState)
        last_30_days = datetime.date.today() - datetime.timedelta(days=30)
        recent_sales = sorted(
            [
                s
                for s in ts.milk_sales
                if (d := self._parse_date(s.get("date"))) is not None
                and d >= last_30_days
            ],
            key=lambda s: s["date"],
        )
        return [
            {
                "day": datetime.date.fromisoformat(s["date"]).strftime("%b %d"),
                "snf_percentage": s["snf_percentage"],
            }
            for s in recent_sales
        ]

    @rx.event
    def on_pie_mouse_enter(self, payload: dict | None = None):
        if payload and payload.get("payload"):
            data = payload["payload"]
            self.active_pie_slice_name = data.get("name", "")
            self.active_pie_slice_value = f"₹{data.get('value', 0)}"
        else:
            self.active_pie_slice_name = ""
            self.active_pie_slice_value = ""

    @rx.event
    def on_pie_mouse_leave(self):
        self.active_pie_slice_name = ""
        self.active_pie_slice_value = ""

import reflex as rx
from typing import TypedDict
import datetime
from app.states.transaction_state import TransactionState, MilkSale
from collections import defaultdict


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


class ProfitLossData(TypedDict):
    month: str
    profit: int
    loss: int


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


class DashboardState(rx.State):
    """Manages the state for the main dashboard."""

    summary_metrics: list[SummaryMetric] = [
        {
            "title": "Total Income",
            "icon": "trending-up",
            "value": "$12,450",
            "change": "+15.2%",
            "change_type": "up",
        },
        {
            "title": "Total Expenses",
            "icon": "trending-down",
            "value": "$7,820",
            "change": "+5.1%",
            "change_type": "down",
        },
        {
            "title": "Net Profit",
            "icon": "dollar-sign",
            "value": "$4,630",
            "change": "+23.8%",
            "change_type": "up",
        },
        {
            "title": "Milk Output (Today)",
            "icon": "droplets",
            "value": "212 Liters",
            "change": "-2.1%",
            "change_type": "down",
        },
        {
            "title": "Feed Cost (Month)",
            "icon": "wheat",
            "value": "$1,250",
            "change": "+1.5%",
            "change_type": "down",
        },
    ]
    expense_data: list[ExpenseData] = [
        {"name": "Feed", "value": 400, "fill": "#10b981"},
        {"name": "Medicine", "value": 300, "fill": "#f97316"},
        {"name": "Labor", "value": 300, "fill": "#3b82f6"},
        {"name": "Utilities", "value": 200, "fill": "#f59e0b"},
        {"name": "Other", "value": 278, "fill": "#8b5cf6"},
    ]
    profit_loss_data: list[ProfitLossData] = [
        {"month": "Jan", "profit": 4000, "loss": 2400},
        {"month": "Feb", "profit": 3000, "loss": 1398},
        {"month": "Mar", "profit": 2000, "loss": 9800},
        {"month": "Apr", "profit": 2780, "loss": 3908},
        {"month": "May", "profit": 1890, "loss": 4800},
        {"month": "Jun", "profit": 2390, "loss": 3800},
    ]
    milk_production_data: list[MilkData] = [
        {"day": "Mon", "liters": 180},
        {"day": "Tue", "liters": 210},
        {"day": "Wed", "liters": 200},
        {"day": "Thu", "liters": 225},
        {"day": "Fri", "liters": 205},
        {"day": "Sat", "liters": 230},
        {"day": "Sun", "liters": 215},
    ]
    weather_highlight: WeatherHighlight = {
        "temp": "28°C",
        "condition": "Sunny",
        "icon": "sun",
        "tip": "Perfect day for harvesting. Low humidity.",
    }
    reminders: list[Reminder] = [
        {"task": "Vaccinate Cattle #43", "due": "In 2 days", "icon": "syringe"},
        {"task": "Restock fertilizer", "due": "This Friday", "icon": "package"},
        {"task": "Check irrigation system", "due": "By weekend", "icon": "wrench"},
    ]
    active_pie_slice_name: str = ""
    active_pie_slice_value: str = ""

    @rx.var
    async def total_coconuts_sold_month(self) -> int:
        ts = await self.get_state(TransactionState)
        today = datetime.date.today()
        current_month_sales = [
            s
            for s in ts.coconut_sales
            if datetime.date.fromisoformat(s["date"]).month == today.month
            and datetime.date.fromisoformat(s["date"]).year == today.year
        ]
        return sum((s["coconut_count"] for s in current_month_sales))

    @rx.var
    async def coconut_revenue_month(self) -> float:
        ts = await self.get_state(TransactionState)
        today = datetime.date.today()
        current_month_sales = [
            s
            for s in ts.coconut_sales
            if datetime.date.fromisoformat(s["date"]).month == today.month
            and datetime.date.fromisoformat(s["date"]).year == today.year
        ]
        return sum((s["total_amount"] for s in current_month_sales))

    @rx.var
    async def avg_fat_percentage_week(self) -> float:
        ts = await self.get_state(TransactionState)
        last_week = datetime.date.today() - datetime.timedelta(days=7)
        recent_sales = [
            s
            for s in ts.milk_sales
            if datetime.date.fromisoformat(s["date"]) >= last_week
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
            if datetime.date.fromisoformat(s["date"]) >= last_week
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
            sale_date = datetime.date.fromisoformat(sale["date"])
            if (today.year - sale_date.year) * 12 + (today.month - sale_date.month) < 6:
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
                if datetime.date.fromisoformat(s["date"]) >= last_30_days
            ],
            key=lambda s: s["date"],
        )
        return [
            {
                "day": datetime.datetime.fromisoformat(s["date"]).strftime("%b %d"),
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
                if datetime.date.fromisoformat(s["date"]) >= last_30_days
            ],
            key=lambda s: s["date"],
        )
        return [
            {
                "day": datetime.datetime.fromisoformat(s["date"]).strftime("%b %d"),
                "snf_percentage": s["snf_percentage"],
            }
            for s in recent_sales
        ]

    @rx.event
    def on_pie_mouse_enter(self, payload: dict | None = None):
        if payload and payload.get("payload"):
            data = payload["payload"]
            self.active_pie_slice_name = data.get("name", "")
            self.active_pie_slice_value = f"${data.get('value', 0)}"
        else:
            self.active_pie_slice_name = ""
            self.active_pie_slice_value = ""

    @rx.event
    def on_pie_mouse_leave(self):
        self.active_pie_slice_name = ""
        self.active_pie_slice_value = ""
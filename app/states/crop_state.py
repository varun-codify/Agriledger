import datetime
import logging
import time
import uuid
from collections import defaultdict
from typing import TypedDict

import httpx
import reflex as rx

_WEATHER_CACHE: dict | None = None
_WEATHER_CACHE_TIME: float = 0.0


from app.database import crud
from app.states.auth_state import AuthState
from app.database.models import (
    ActivityType,
    Crop,
    CropActivity,
    HarvestRecord,
)


class CurrentWeather(TypedDict):
    temperature_2m: float
    relative_humidity_2m: int
    precipitation: float
    weather_code: int
    wind_speed_10m: float


class DailyWeather(TypedDict):
    time: list[str]
    weather_code: list[int]
    temperature_2m_max: list[float]
    temperature_2m_min: list[float]
    precipitation_sum: list[float]
    precipitation_probability_max: list[int]


class WeatherData(TypedDict):
    current: CurrentWeather
    daily: DailyWeather


class FarmingSuggestion(TypedDict):
    title: str
    suggestion: str
    icon: str
    color: str


def _clean_weather_data(raw: dict) -> WeatherData:
    """Reduce an open-meteo response to exactly the declared WeatherData keys.

    Reflex validates state vars assigned against their declared TypedDict and
    logs a mismatch for every undeclared key (latitude, timezone,
    current_units, current.time, ...). Picking the declared fields here keeps
    the stored state clean and shrinks the payload sent to the browser.
    """
    current = raw.get("current") or {}
    daily = raw.get("daily") or {}

    def _int(v) -> int:
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0

    def _float(v) -> float:
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    return {
        "current": {
            "temperature_2m": _float(current.get("temperature_2m")),
            "relative_humidity_2m": _int(current.get("relative_humidity_2m")),
            "precipitation": _float(current.get("precipitation")),
            "weather_code": _int(current.get("weather_code")),
            "wind_speed_10m": _float(current.get("wind_speed_10m")),
        },
        "daily": {
            "time": [str(t) for t in (daily.get("time") or [])],
            "weather_code": [_int(c) for c in (daily.get("weather_code") or [])],
            "temperature_2m_max": [
                _float(v) for v in (daily.get("temperature_2m_max") or [])
            ],
            "temperature_2m_min": [
                _float(v) for v in (daily.get("temperature_2m_min") or [])
            ],
            "precipitation_sum": [
                _float(v) for v in (daily.get("precipitation_sum") or [])
            ],
            "precipitation_probability_max": [
                _int(v) for v in (daily.get("precipitation_probability_max") or [])
            ],
        },
    }


def _normalize_iso_date(raw: str) -> str | None:
    """Normalize a date submitted by a browser into ISO (YYYY-MM-DD)."""
    value = (raw or "").strip()
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(value).isoformat()
    except ValueError:
        pass
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


# Demo rows seeded into a farm's collection on first load. Kept as a
# module-level constant (not a state var) so it is never serialized to the
# browser — state base vars are sent to every client on every page load.
DEMO_CROPS_DATA: list[Crop] = [
    {
        "id": "crop1",
        "name": "Corn",
        "field_name": "Field A",
        "planting_date": "2024-04-15",
        "status": "Growing",
        "image_url": "https://api.dicebear.com/9.x/shapes/svg?seed=Corn",
        "activities": [
            {
                "id": "a1",
                "date": "2024-04-15",
                "activity_type": "Planting",
                "notes": "Planted 10 acres of corn.",
                "cost": 500.0,
            },
            {
                "id": "a2",
                "date": "2024-05-20",
                "activity_type": "Fertilizing",
                "notes": "Applied nitrogen fertilizer.",
                "cost": 350.0,
            },
        ],
        "harvests": [],
        "farm_id": "demo-farm",
    },
    {
        "id": "crop2",
        "name": "Wheat",
        "field_name": "Field B",
        "planting_date": "2023-10-01",
        "status": "Harvested",
        "image_url": "https://api.dicebear.com/9.x/shapes/svg?seed=Wheat",
        "activities": [
            {
                "id": "a3",
                "date": "2023-10-01",
                "activity_type": "Planting",
                "notes": "Planted 20 acres of wheat.",
                "cost": 800.0,
            }
        ],
        "harvests": [
            {
                "id": "h1",
                "date": "2024-03-10",
                "quantity": 1000,
                "unit": "bushels",
                "income": 7000.0,
            }
        ],
    },
]


WEATHER_CODES = {
    0: ("Clear sky", "sun"),
    1: ("Mainly clear", "sun"),
    2: ("Partly cloudy", "cloud-sun"),
    3: ("Overcast", "cloud"),
    45: ("Fog", "cloudy"),
    48: ("Depositing rime fog", "cloudy"),
    51: ("Light drizzle", "cloud-drizzle"),
    53: ("Moderate drizzle", "cloud-drizzle"),
    55: ("Dense drizzle", "cloud-drizzle"),
    56: ("Light freezing drizzle", "cloud-drizzle"),
    57: ("Dense freezing drizzle", "cloud-drizzle"),
    61: ("Slight rain", "cloud-rain"),
    63: ("Moderate rain", "cloud-rain"),
    65: ("Heavy rain", "cloud-rain-heavy"),
    66: ("Light freezing rain", "cloud-rain-heavy"),
    67: ("Heavy freezing rain", "cloud-rain-heavy"),
    71: ("Slight snow fall", "cloud-snow"),
    73: ("Moderate snow fall", "cloud-snow"),
    75: ("Heavy snow fall", "cloud-snow"),
    77: ("Snow grains", "cloud-snow"),
    80: ("Slight rain showers", "cloud-lightning-rain"),
    81: ("Moderate rain showers", "cloud-lightning-rain"),
    82: ("Violent rain showers", "cloud-lightning-rain"),
    85: ("Slight snow showers", "cloud-snow"),
    86: ("Heavy snow showers", "cloud-snow"),
    95: ("Thunderstorm", "cloud-lightning"),
    96: ("Thunderstorm with slight hail", "cloud-hail"),
    99: ("Thunderstorm with heavy hail", "cloud-hail"),
}


class CropState(rx.State):
    """Manages the state for crop management."""

    crops_list: list[Crop] = []
    current_crop: Crop | None = None
    profile_loading: bool = True
    profile_active_tab: str = "Overview"
    current_dialog_date: str = datetime.date.today().isoformat()
    show_add_crop_dialog: bool = False
    show_add_activity_dialog: bool = False
    show_add_harvest_dialog: bool = False
    add_crop_error: str = ""
    dialog_error: str = ""
    weather_data: WeatherData | None = None
    weather_loading: bool = True
    activity_types: list[ActivityType] = [
        "Planting",
        "Fertilizing",
        "Pesticide Application",
        "Irrigation",
        "Weeding",
        "Harvesting",
        "Expense",
    ]

    @rx.event
    def load_crop_profile(self):
        self.profile_loading = True
        self.profile_active_tab = "Overview"
        yield
        crop_id = self.router.page.params.get("id", "")
        found_crop = next((c for c in self.crops_list if c["id"] == crop_id), None)
        self.current_crop = found_crop
        self.profile_loading = False

    @rx.event
    def toggle_add_crop_dialog(self, open: bool):
        self.show_add_crop_dialog = open
        if open:
            self.add_crop_error = ""

    @rx.event
    async def fetch_crops_list(self):
        """Fetches crops list from DB (seeds demo data per-farm if empty)."""
        auth = await self.get_state(AuthState)
        await crud.ensure_farm_seed("crops", auth.farm_id, DEMO_CROPS_DATA)
        self.crops_list = await crud.get_all_crops(farm_id=auth.farm_id)

    @rx.event
    async def add_crop(self, form_data: dict):
        name = str(form_data.get("name", "")).strip()
        field_name = str(form_data.get("field_name", "")).strip()
        planting_date = str(form_data.get("planting_date", "")).strip()
        initial_cost_raw = str(form_data.get("initial_cost", "")).strip()

        if not name:
            self.add_crop_error = "Crop name is required."
            return
        if not field_name:
            self.add_crop_error = "Field name is required."
            return
        if not planting_date:
            self.add_crop_error = "Planting date is mandatory."
            return
        iso_planting_date = _normalize_iso_date(planting_date)
        if not iso_planting_date:
            self.add_crop_error = "Planting date must be a valid date."
            return
        initial_cost = 0.0
        if initial_cost_raw:
            try:
                initial_cost = float(initial_cost_raw)
            except ValueError:
                self.add_crop_error = "Initial cost must be a valid number."
                return
        new_crop: Crop = {
            "id": str(uuid.uuid4()),
            "name": name,
            "field_name": field_name,
            "planting_date": iso_planting_date,
            "status": "Planted",
            "image_url": f"https://api.dicebear.com/9.x/shapes/svg?seed={name}",
            "activities": [
                {
                    "id": str(uuid.uuid4()),
                    "date": iso_planting_date,
                    "activity_type": "Planting",
                    "notes": "Initial planting.",
                    "cost": initial_cost,
                }
            ],
            "harvests": [],
            "farm_id": (await self.get_state(AuthState)).farm_id,
        }
        success = await crud.create_crop(new_crop)
        if success:
            self.crops_list.append(new_crop)
            self.add_crop_error = ""
            self.toggle_add_crop_dialog(False)
            return rx.toast.success(f"'{new_crop['name']}' has been added.")
        self.add_crop_error = "Failed to save crop. Please try again."

    @rx.event(background=True)
    async def fetch_weather(self):
        global _WEATHER_CACHE, _WEATHER_CACHE_TIME
        now = time.time()
        if _WEATHER_CACHE is not None and (now - _WEATHER_CACHE_TIME < 900):
            async with self:
                self.weather_data = _WEATHER_CACHE
                self.weather_loading = False
            return

        async with self:
            self.weather_loading = True
        try:
            lat, lon = (28.6139, 77.209)
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
                "timezone": "auto",
            }
            async with httpx.AsyncClient(timeout=4.0) as client:
                response = await client.get(
                    "https://api.open-meteo.com/v1/forecast", params=params
                )
                response.raise_for_status()
                data = response.json()
                cleaned = _clean_weather_data(data)
                _WEATHER_CACHE = cleaned
                _WEATHER_CACHE_TIME = now
                async with self:
                    self.weather_data = cleaned
                    self.weather_loading = False
        except Exception as e:
            logging.exception(f"Failed to fetch weather data: {e}")
            async with self:
                self.weather_loading = False


    def _get_weather_info(self, code: int) -> tuple[str, str]:
        return WEATHER_CODES.get(code, ("Unknown", "cloud-question"))

    @rx.var
    def current_weather_info(self) -> tuple[str, str]:
        if self.weather_data:
            return self._get_weather_info(self.weather_data["current"]["weather_code"])
        return ("Unknown", "cloud-question")

    @rx.var
    def farming_suggestions(self) -> list[FarmingSuggestion]:
        if not self.weather_data:
            return []
        suggestions = []
        tomorrow_precip_prob = self.weather_data["daily"][
            "precipitation_probability_max"
        ][1]
        tomorrow_temp_max = self.weather_data["daily"]["temperature_2m_max"][1]
        if tomorrow_precip_prob > 50:
            suggestions.append(
                {
                    "title": "Rain Expected",
                    "suggestion": f"High chance of rain tomorrow ({tomorrow_precip_prob}%). Consider postponing pesticide application or irrigation.",
                    "icon": "cloud-rain",
                    "color": "blue",
                }
            )
        else:
            suggestions.append(
                {
                    "title": "Good Weather for Field Work",
                    "suggestion": f"Low chance of rain tomorrow ({tomorrow_precip_prob}%). It's a good day for spraying or other field activities.",
                    "icon": "sun",
                    "color": "yellow",
                }
            )
        if tomorrow_temp_max > 35:
            suggestions.append(
                {
                    "title": "High Temperatures",
                    "suggestion": f"Expect high temperatures up to {tomorrow_temp_max}°C. Ensure crops and livestock have adequate water.",
                    "icon": "thermometer-sun",
                    "color": "orange",
                }
            )
        return suggestions

    @rx.var
    def daily_forecast_data(self) -> list[dict]:
        if not self.weather_data:
            return []
        daily = self.weather_data["daily"]
        data = []
        for i in range(7):
            day_name = datetime.datetime.fromisoformat(daily["time"][i]).strftime("%a")
            weather_info = self._get_weather_info(daily["weather_code"][i])
            data.append(
                {
                    "day": day_name,
                    "icon": weather_info[1],
                    "max_temp": round(daily["temperature_2m_max"][i]),
                    "min_temp": round(daily["temperature_2m_min"][i]),
                    "precip_prob": daily["precipitation_probability_max"][i],
                }
            )
        return data

    @rx.event
    def set_profile_tab(self, tab: str):
        self.profile_active_tab = tab

    @rx.event
    def toggle_add_activity_dialog(self, open: bool):
        self.show_add_activity_dialog = open
        if open:
            self.current_dialog_date = datetime.date.today().isoformat()
        self.dialog_error = ""

    @rx.event
    def toggle_add_harvest_dialog(self, open: bool):
        self.show_add_harvest_dialog = open
        if open:
            self.current_dialog_date = datetime.date.today().isoformat()
        self.dialog_error = ""

    @rx.event
    async def add_activity(self, form_data: dict):
        if not self.current_crop:
            return rx.toast.error("No crop selected.")
        date = str(form_data.get("date", "")).strip()
        activity_type = str(form_data.get("activity_type", "")).strip()
        cost_raw = str(form_data.get("cost", "")).strip()
        if not date:
            self.dialog_error = "Date is mandatory."
            return
        if not activity_type:
            self.dialog_error = "Please select an activity type."
            return
        cost = 0.0
        if cost_raw:
            try:
                cost = float(cost_raw)
            except ValueError:
                self.dialog_error = "Cost must be a valid number."
                return
        new_activity: CropActivity = {
            "id": str(uuid.uuid4()),
            "date": date,
            "activity_type": activity_type,
            "notes": form_data.get("notes", ""),
            "cost": cost,
        }
        self.current_crop["activities"].insert(0, new_activity)
        await crud.update_crop(
            self.current_crop["id"], {"activities": self.current_crop["activities"]}
        )
        for i, c in enumerate(self.crops_list):
            if c["id"] == self.current_crop["id"]:
                self.crops_list[i] = self.current_crop
                break
        self.dialog_error = ""
        self.toggle_add_activity_dialog(False)
        return rx.toast.success(
            f"Activity '{new_activity['activity_type']}' added."
        )

    @rx.event
    async def add_harvest(self, form_data: dict):
        if not self.current_crop:
            return rx.toast.error("No crop selected.")
        date = str(form_data.get("date", "")).strip()
        quantity_raw = str(form_data.get("quantity", "")).strip()
        unit = str(form_data.get("unit", "kg")).strip()
        income_raw = str(form_data.get("income", "")).strip()
        if not date:
            self.dialog_error = "Date is mandatory."
            return
        if not quantity_raw:
            self.dialog_error = "Quantity is mandatory."
            return
        try:
            quantity = float(quantity_raw)
        except ValueError:
            self.dialog_error = "Quantity must be a valid number."
            return
        income = 0.0
        if income_raw:
            try:
                income = float(income_raw)
            except ValueError:
                self.dialog_error = "Income must be a valid number."
                return
        new_harvest: HarvestRecord = {
            "id": str(uuid.uuid4()),
            "date": date,
            "quantity": quantity,
            "unit": unit,
            "income": income,
        }
        self.current_crop["harvests"].insert(0, new_harvest)
        if self.current_crop["status"] != "Harvested":
            self.current_crop["status"] = "Harvested"
        await crud.update_crop(
            self.current_crop["id"],
            {
                "harvests": self.current_crop["harvests"],
                "status": self.current_crop["status"],
            },
        )
        for i, c in enumerate(self.crops_list):
            if c["id"] == self.current_crop["id"]:
                self.crops_list[i] = self.current_crop
                break
        self.dialog_error = ""
        self.toggle_add_harvest_dialog(False)
        return rx.toast.success("Harvest record added.")

    @rx.var
    def days_since_planting(self) -> int:
        if not self.current_crop:
            return 0
        iso = _normalize_iso_date(self.current_crop.get("planting_date", ""))
        if not iso:
            return 0
        planting_date = datetime.date.fromisoformat(iso)
        return (datetime.date.today() - planting_date).days

    @rx.var
    def total_investment(self) -> float:
        return sum(
            (
                act["cost"]
                for crop in self.crops_list
                for act in crop["activities"]
                if act["activity_type"] == "Planting"
            )
        )

    @rx.var
    def total_expenses(self) -> float:
        if not self.current_crop:
            return 0.0
        return sum((act["cost"] for act in self.current_crop["activities"]))

    @rx.var
    def total_harvest_income(self) -> float:
        if not self.current_crop:
            return 0.0
        return sum((harv["income"] for harv in self.current_crop["harvests"]))

    @rx.var
    def profitability(self) -> float:
        return self.total_harvest_income - self.total_expenses

    @rx.var
    def expense_breakdown(self) -> list[dict]:
        if not self.current_crop:
            return []
        expense_map = defaultdict(float)
        for activity in self.current_crop["activities"]:
            expense_map[activity["activity_type"]] += activity["cost"]
        colors = {
            "Planting": "#10b981",
            "Fertilizing": "#3b82f6",
            "Pesticide Application": "#f97316",
            "Irrigation": "#06b6d4",
            "Weeding": "#f59e0b",
            "Harvesting": "#8b5cf6",
            "Expense": "#64748b",
        }
        return [
            {"name": type, "value": cost, "fill": colors.get(type, "#cccccc")}
            for type, cost in expense_map.items()
        ]

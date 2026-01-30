import reflex as rx
from typing import TypedDict, Literal
import datetime
import uuid
import logging
import httpx
from collections import defaultdict
from app.database import crud
from app.database.models import (
    Crop,
    CropActivity,
    HarvestRecord,
    ActivityType,
    CropStatus,
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
    current_crop: Crop | None = None
    profile_loading: bool = True
    profile_active_tab: str = "Overview"
    current_dialog_date: str = datetime.date.today().isoformat()
    show_add_crop_dialog: bool = False
    show_add_activity_dialog: bool = False
    show_add_harvest_dialog: bool = False
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

    @rx.event
    async def fetch_crops_list(self):
        """Fetches crops list from DB."""
        crud.init_database_seeds({"crops": self.DEMO_CROPS_DATA})
        self.crops_list = await crud.get_all_crops()

    @rx.event
    async def add_crop(self, form_data: dict):
        if not form_data.get("name") or not form_data.get("field_name"):
            return rx.toast.error("Crop name and field name are required.")
        new_crop: Crop = {
            "id": str(uuid.uuid4()),
            "name": form_data["name"],
            "field_name": form_data["field_name"],
            "planting_date": form_data["planting_date"],
            "status": "Planted",
            "image_url": f"https://api.dicebear.com/9.x/shapes/svg?seed={form_data['name']}",
            "activities": [
                {
                    "id": str(uuid.uuid4()),
                    "date": form_data["planting_date"],
                    "activity_type": "Planting",
                    "notes": "Initial planting.",
                    "cost": float(form_data.get("initial_cost", 0.0)),
                }
            ],
            "harvests": [],
        }
        success = await crud.create_crop(new_crop)
        if success:
            self.crops_list.append(new_crop)
            self.toggle_add_crop_dialog(False)
            return rx.toast.success(f"'{new_crop['name']}' has been added.")
        return rx.toast.error("Failed to save crop.")

    @rx.event(background=True)
    async def fetch_weather(self):
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
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.open-meteo.com/v1/forecast", params=params
                )
                response.raise_for_status()
                data = response.json()
                async with self:
                    self.weather_data = data
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

    @rx.event
    def toggle_add_harvest_dialog(self, open: bool):
        self.show_add_harvest_dialog = open
        if open:
            self.current_dialog_date = datetime.date.today().isoformat()

    @rx.event
    async def add_activity(self, form_data: dict):
        if not self.current_crop:
            return rx.toast.error("No crop selected.")
        try:
            new_activity: CropActivity = {
                "id": str(uuid.uuid4()),
                "date": form_data["date"],
                "activity_type": form_data["activity_type"],
                "notes": form_data.get("notes", ""),
                "cost": float(form_data.get("cost", 0.0)),
            }
            self.current_crop["activities"].insert(0, new_activity)
            await crud.update_crop(
                self.current_crop["id"], {"activities": self.current_crop["activities"]}
            )
            for i, c in enumerate(self.crops_list):
                if c["id"] == self.current_crop["id"]:
                    self.crops_list[i] = self.current_crop
                    break
            self.toggle_add_activity_dialog(False)
            return rx.toast.success(
                f"Activity '{new_activity['activity_type']}' added."
            )
        except (ValueError, KeyError) as e:
            logging.exception(f"Error adding activity: {e}")
            return rx.toast.error(f"Invalid data: {e}")

    @rx.event
    async def add_harvest(self, form_data: dict):
        if not self.current_crop:
            return rx.toast.error("No crop selected.")
        try:
            new_harvest: HarvestRecord = {
                "id": str(uuid.uuid4()),
                "date": form_data["date"],
                "quantity": float(form_data.get("quantity", 0.0)),
                "unit": form_data.get("unit", "kg"),
                "income": float(form_data.get("income", 0.0)),
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
            self.toggle_add_harvest_dialog(False)
            return rx.toast.success(f"Harvest record added.")
        except (ValueError, KeyError) as e:
            logging.exception(f"Error adding harvest: {e}")
            return rx.toast.error(f"Invalid data: {e}")

    @rx.var
    def days_since_planting(self) -> int:
        if not self.current_crop:
            return 0
        planting_date = datetime.date.fromisoformat(self.current_crop["planting_date"])
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
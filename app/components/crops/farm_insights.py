import reflex as rx

from app.states.crop_state import CropState


def current_weather_card() -> rx.Component:
    return rx.cond(
        CropState.weather_data,
        rx.el.div(
            rx.el.h3("Current Weather", class_name="font-semibold text-stone-800 dark:text-stone-100"),
            rx.el.div(
                rx.icon(
                    CropState.current_weather_info[1],
                    class_name="h-16 w-16 text-yellow-500",
                ),
                rx.el.div(
                    rx.el.p(
                        f"{CropState.weather_data['current']['temperature_2m']}°C",
                        class_name="text-4xl font-bold text-stone-800 dark:text-stone-100",
                    ),
                    rx.el.p(
                        CropState.current_weather_info[0],
                        class_name="text-stone-600 font-medium dark:text-stone-300",
                    ),
                ),
                class_name="flex items-center gap-4 mt-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("wind", class_name="h-4 w-4 text-stone-500 dark:text-stone-400"),
                    rx.el.span(
                        f"{CropState.weather_data['current']['wind_speed_10m']} km/h",
                        class_name="text-sm",
                    ),
                    class_name="flex items-center gap-2 text-stone-600 dark:text-stone-300",
                ),
                rx.el.div(
                    rx.icon("droplets", class_name="h-4 w-4 text-stone-500 dark:text-stone-400"),
                    rx.el.span(
                        f"{CropState.weather_data['current']['relative_humidity_2m']}%",
                        class_name="text-sm",
                    ),
                    class_name="flex items-center gap-2 text-stone-600 dark:text-stone-300",
                ),
                rx.el.div(
                    rx.icon("umbrella", class_name="h-4 w-4 text-stone-500 dark:text-stone-400"),
                    rx.el.span(
                        f"{CropState.weather_data['current']['precipitation']} mm",
                        class_name="text-sm",
                    ),
                    class_name="flex items-center gap-2 text-stone-600 dark:text-stone-300",
                ),
                class_name="grid grid-cols-3 gap-2 mt-4 text-center",
            ),
            class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700",
        ),
        rx.el.div(
            class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 animate-pulse h-48 dark:bg-stone-900 dark:border-stone-700"
        ),
    )


def daily_forecast_card(day_data: dict[str, str | int]) -> rx.Component:
    return rx.el.div(
        rx.el.p(day_data["day"], class_name="font-semibold text-sm text-stone-600 dark:text-stone-300"),
        rx.icon(
            day_data["icon"].to(str), class_name="h-8 w-8 my-2 text-yellow-500 mx-auto"
        ),
        rx.el.p(
            f"{day_data['max_temp']}° / {day_data['min_temp']}°",
            class_name="font-bold text-stone-800 dark:text-stone-100",
        ),
        rx.el.div(
            rx.icon("umbrella", class_name="h-3 w-3 text-blue-500"),
            rx.el.p(f"{day_data['precip_prob']}%", class_name="text-xs text-blue-600"),
            class_name="flex items-center gap-1 justify-center mt-1",
        ),
        class_name="text-center p-3 bg-stone-50/50 rounded-xl dark:bg-stone-800",
    )


def weather_forecast_section() -> rx.Component:
    return rx.cond(
        CropState.weather_data,
        rx.el.div(
            rx.el.h3("7-Day Forecast", class_name="font-semibold text-stone-800 mb-4 dark:text-stone-100"),
            rx.el.div(
                rx.foreach(CropState.daily_forecast_data, daily_forecast_card),
                class_name="grid grid-cols-3 md:grid-cols-7 gap-3",
            ),
            class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-2 dark:bg-stone-900 dark:border-stone-700",
        ),
        rx.el.div(
            class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-100 col-span-2 animate-pulse h-48 dark:bg-stone-900 dark:border-stone-700"
        ),
    )


def suggestion_card(suggestion: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(suggestion["icon"], class_name="h-6 w-6"),
            class_name=f"p-3 rounded-full bg-{suggestion['color']}-100 text-{suggestion['color']}-600",
        ),
        rx.el.div(
            rx.el.p(suggestion["title"], class_name="font-semibold text-stone-800 dark:text-stone-100"),
            rx.el.p(suggestion["suggestion"], class_name="text-sm text-stone-600 dark:text-stone-300"),
        ),
        class_name="flex items-start gap-4 p-4 bg-white rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700",
    )


def farm_insights_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            current_weather_card(),
            weather_forecast_section(),
            class_name="grid grid-cols-1 lg:grid-cols-3 gap-6",
        ),
        rx.el.div(
            rx.el.h2(
                "Farming Suggestions",
                class_name="text-2xl font-bold text-stone-800 dark:text-stone-100 my-6 dark:text-stone-100",
            ),
            rx.cond(
                CropState.weather_loading,
                rx.el.div(
                    "Loading suggestions...", class_name="text-center text-stone-500 dark:text-stone-400"
                ),
                rx.el.div(
                    rx.foreach(CropState.farming_suggestions, suggestion_card),
                    class_name="space-y-4",
                ),
            ),
        ),
        on_mount=CropState.fetch_weather,
    )

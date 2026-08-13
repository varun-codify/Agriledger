"""Settings page with profile, farm details, preferences, i18n, and notifications."""

import reflex as rx

from app.components.common import install_app_button
from app.components.layout import dashboard_layout
from app.config import config
from app.states.auth_state import AuthState
from app.states.ui_state import UIState


# Server-side truth for the Integrations panel: True when a Gemini API key is
# configured (evaluated once at import time, so it reflects the running .env).
GEMINI_ACTIVE = config.gemini.is_configured
# The model name the AI features will try first (the one shown as active).
GEMINI_MODEL_NAME = config.gemini.model
from app.states.i18n_state import I18nState
from app.states.notification_state import NotificationState
from app.states.settings_state import SettingsState


def setting_toggle(
    label: str,
    description: str,
    checked: rx.Var[bool],
    on_change: rx.event.EventHandler,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h4(label, class_name="font-medium text-stone-800"),
            rx.el.p(description, class_name="text-sm text-stone-500"),
        ),
        rx.el.input(
            type="checkbox",
            checked=checked,
            on_change=on_change,
            class_name="w-5 h-5 text-emerald-600 rounded focus:ring-emerald-500",
        ),
        class_name="flex items-center justify-between py-4 border-b border-stone-100 last:border-0",
    )


def profile_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Profile Settings", class_name="text-lg font-semibold text-stone-800 mb-4"
        ),
        rx.cond(
            SettingsState.settings_error != "",
            rx.el.div(
                rx.icon("triangle-alert", class_name="h-4 w-4 mr-2 flex-shrink-0"),
                SettingsState.settings_error,
                class_name="flex items-start text-red-600 text-sm bg-red-50 border border-red-200 p-3 rounded-lg mb-4",
            ),
            None,
        ),
        rx.el.form(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Full Name",
                        class_name="block text-sm font-medium text-stone-700 mb-1",
                    ),
                    rx.el.input(
                        name="name",
                        default_value=AuthState.current_user["name"],
                        class_name="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Email Address",
                        class_name="block text-sm font-medium text-stone-700 mb-1",
                    ),
                    rx.el.input(
                        name="email",
                        type="email",
                        default_value=AuthState.current_user["email"],
                        disabled=True,
                        class_name="w-full px-4 py-2 border rounded-lg bg-stone-50 text-stone-500",
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
            ),
            rx.el.button(
                "Update Profile",
                type="submit",
                class_name="mt-4 px-4 py-2 bg-emerald-500 text-white rounded-lg font-semibold hover:bg-emerald-600 transition",
            ),
            on_submit=SettingsState.update_profile,
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 mb-6",
    )


def farm_details_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Farm Details", class_name="text-lg font-semibold text-stone-800 mb-4"
        ),
        rx.cond(
            SettingsState.settings_error != "",
            rx.el.div(
                rx.icon("triangle-alert", class_name="h-4 w-4 mr-2 flex-shrink-0"),
                SettingsState.settings_error,
                class_name="flex items-start text-red-600 text-sm bg-red-50 border border-red-200 p-3 rounded-lg mb-4",
            ),
            None,
        ),
        rx.el.form(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Farm Name",
                        class_name="block text-sm font-medium text-stone-700 mb-1",
                    ),
                    rx.el.input(
                        name="farm_name",
                        default_value=SettingsState.farm_name,
                        class_name="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Location",
                        class_name="block text-sm font-medium text-stone-700 mb-1",
                    ),
                    rx.el.input(
                        name="farm_location",
                        default_value=SettingsState.farm_location,
                        class_name="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Farm Size",
                        class_name="block text-sm font-medium text-stone-700 mb-1",
                    ),
                    rx.el.input(
                        name="farm_size",
                        default_value=SettingsState.farm_size,
                        class_name="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-500",
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
            ),
            rx.el.button(
                "Save Farm Details",
                type="submit",
                class_name="mt-4 px-4 py-2 bg-emerald-500 text-white rounded-lg font-semibold hover:bg-emerald-600 transition",
            ),
            on_submit=SettingsState.update_farm_details,
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 mb-6",
    )


def notification_settings_section() -> rx.Component:
    """Email & SMS notification preferences."""
    return rx.el.div(
        rx.el.h3(
            "Notification Preferences",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        setting_toggle(
            "Email Notifications",
            "Receive alerts and reports via email.",
            SettingsState.email_alerts,
            lambda v: SettingsState.update_notification_settings("email", v),
        ),
        setting_toggle(
            "SMS Alerts",
            "Receive critical alerts (breeding, weather) via SMS.",
            SettingsState.sms_alerts,
            lambda v: SettingsState.update_notification_settings("sms", v),
        ),
        setting_toggle(
            "In-App Notifications",
            "Show alerts within the dashboard.",
            SettingsState.notifications_enabled,
            lambda v: SettingsState.update_notification_settings("notifications", v),
        ),
        rx.el.div(
            rx.el.h4(
                "Upcoming Reminders",
                class_name="font-medium text-stone-800 mb-3 mt-4",
            ),
            rx.el.div(
                rx.cond(
                    NotificationState.notifications.length() == 0,
                    rx.el.p(
                        "No pending notifications.",
                        class_name="text-sm text-stone-400 py-4",
                    ),
                    rx.el.div(
                        rx.foreach(
                            NotificationState.notifications,
                            lambda n: rx.el.div(
                                rx.el.div(
                                    rx.el.p(
                                        n["title"],
                                        class_name="font-medium text-stone-700 text-sm",
                                    ),
                                    rx.el.p(
                                        n.get("message", ""),
                                        class_name="text-xs text-stone-500",
                                    ),
                                ),
                                class_name="p-3 bg-stone-50 rounded-lg mb-2",
                            ),
                        ),
                    ),
                ),
            ),
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 mb-6",
    )


def language_section() -> rx.Component:
    """Language selection with i18n support."""
    return rx.el.div(
        rx.el.h3(
            "Language / மொழी / भाषा",
            class_name="text-lg font-semibold text-stone-800 mb-4",
        ),
        rx.el.div(
            rx.el.button(
                "English",
                on_click=lambda: I18nState.set_language("English"),
                class_name=rx.cond(
                    I18nState.language == "English",
                    "px-6 py-3 rounded-xl bg-emerald-500 text-white font-semibold shadow-sm transition-all",
                    "px-6 py-3 rounded-xl bg-white text-stone-600 font-semibold border border-stone-200 hover:bg-stone-50 transition-all",
                ),
            ),
            rx.el.button(
                "தமிழ் (Tamil)",
                on_click=lambda: I18nState.set_language("Tamil"),
                class_name=rx.cond(
                    I18nState.language == "Tamil",
                    "px-6 py-3 rounded-xl bg-emerald-500 text-white font-semibold shadow-sm transition-all",
                    "px-6 py-3 rounded-xl bg-white text-stone-600 font-semibold border border-stone-200 hover:bg-stone-50 transition-all",
                ),
            ),
            rx.el.button(
                "हिन्दी (Hindi)",
                on_click=lambda: I18nState.set_language("Hindi"),
                class_name=rx.cond(
                    I18nState.language == "Hindi",
                    "px-6 py-3 rounded-xl bg-emerald-500 text-white font-semibold shadow-sm transition-all",
                    "px-6 py-3 rounded-xl bg-white text-stone-600 font-semibold border border-stone-200 hover:bg-stone-50 transition-all",
                ),
            ),
            class_name="flex gap-3 flex-wrap",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 mb-6",
    )


def preferences_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Preferences", class_name="text-lg font-semibold text-stone-800 mb-4"),
        setting_toggle(
            "Dark Mode",
            "Switch between light and dark themes.",
            SettingsState.theme_mode == "dark",
            lambda v: SettingsState.toggle_theme(),
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("database-backup", class_name="h-4 w-4 mr-2"),
                "Backup All Data",
                on_click=SettingsState.backup_data,
                class_name="flex items-center px-4 py-2 bg-stone-800 text-white rounded-lg font-semibold hover:bg-stone-900 transition",
            ),
            class_name="pt-4 border-t border-stone-100 mt-4",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 mb-6",
    )


def integrations_section() -> rx.Component:
    """Shows integration status for external services."""
    return rx.el.div(
        rx.el.h3(
            "Integrations", class_name="text-lg font-semibold text-stone-800 mb-4"
        ),
        rx.el.div(
            # Gemini
            rx.el.div(
                rx.icon("brain-circuit", class_name="h-5 w-5 text-stone-500"),
                rx.el.div(
                    rx.el.p("Gemini (AI + Bill Scanning)", class_name="font-medium text-stone-700"),
                    rx.el.p("Powers AI recommendations, the chatbot, and milk-bill photo OCR (fat %, SNF %, litres, amount).", class_name="text-xs text-stone-500"),
                ),
                (
                    rx.el.span(
                        f"Active · {GEMINI_MODEL_NAME}",
                        class_name="text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-700",
                    )
                    if GEMINI_ACTIVE
                    else rx.el.span(
                        "Set GEMINI_API_KEY in .env & restart",
                        class_name="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700",
                    )
                ),
                class_name="flex items-center justify-between py-3 border-b border-stone-100",
            ),
            # Resend
            rx.el.div(
                rx.icon("mail", class_name="h-5 w-5 text-stone-500"),
                rx.el.div(
                    rx.el.p("Resend (Email)", class_name="font-medium text-stone-700"),
                    rx.el.p("Sends reports and alerts via email.", class_name="text-xs text-stone-500"),
                ),
                rx.el.span(
                    "Configure via RESEND_API_KEY",
                    class_name="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700",
                ),
                class_name="flex items-center justify-between py-3 border-b border-stone-100",
            ),
            # Twilio
            rx.el.div(
                rx.icon("smartphone", class_name="h-5 w-5 text-stone-500"),
                rx.el.div(
                    rx.el.p("Twilio (SMS/WhatsApp)", class_name="font-medium text-stone-700"),
                    rx.el.p("Sends breeding and weather alerts via SMS.", class_name="text-xs text-stone-500"),
                ),
                rx.el.span(
                    "Configure via TWILIO_*",
                    class_name="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700",
                ),
                class_name="flex items-center justify-between py-3 border-b border-stone-100",
            ),
            # OpenWeather
            rx.el.div(
                rx.icon("cloud-sun", class_name="h-5 w-5 text-stone-500"),
                rx.el.div(
                    rx.el.p("OpenWeatherMap", class_name="font-medium text-stone-700"),
                    rx.el.p("Weather data uses free Open-Meteo API (no key needed).", class_name="text-xs text-stone-500"),
                ),
                rx.el.span(
                    "Active (Open-Meteo)",
                    class_name="text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-700",
                ),
                class_name="flex items-center justify-between py-3 border-b border-stone-100",
            ),
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100",
    )


def install_section() -> rx.Component:
    """Install the app on this device (uses the browser install prompt)."""
    return rx.cond(
        UIState.install_prompt_available,
        rx.el.div(
            rx.el.h3(
                "Install App", class_name="text-lg font-semibold text-stone-800 mb-4"
            ),
            rx.el.p(
                "Install AgriLedger on this device for a native-app experience — ",
                "fullscreen, with its own icon on your home screen.",
                class_name="text-sm text-stone-500 mb-4",
            ),
            install_app_button(),
            rx.el.p(
                "Tip: on iOS, use your browser's Share → ",
                rx.el.span("Add to Home Screen", class_name="font-medium"),
                ".",
                class_name="text-xs text-stone-400 mt-3",
            ),
            class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 mb-6",
        ),
        None,
    )


def settings_page_content() -> rx.Component:
    return rx.el.div(
        profile_section(),
        farm_details_section(),
        language_section(),
        notification_settings_section(),
        preferences_section(),
        install_section(),
        integrations_section(),
        class_name="max-w-4xl mx-auto",
    )


def settings_page() -> rx.Component:
    return dashboard_layout(settings_page_content(), "Settings")

import reflex as rx
from app.states.settings_state import SettingsState
from app.states.auth_state import AuthState
from app.components.layout import dashboard_layout


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


def preferences_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Preferences", class_name="text-lg font-semibold text-stone-800 mb-4"),
        setting_toggle(
            "Dark Mode",
            "Switch between light and dark themes.",
            SettingsState.theme_mode == "dark",
            lambda v: SettingsState.toggle_theme(),
        ),
        setting_toggle(
            "Email Notifications",
            "Receive alerts via email.",
            SettingsState.email_alerts,
            lambda v: SettingsState.update_notification_settings("email", v),
        ),
        setting_toggle(
            "SMS Alerts",
            "Receive critical alerts via SMS.",
            SettingsState.sms_alerts,
            lambda v: SettingsState.update_notification_settings("sms", v),
        ),
        rx.el.div(
            rx.el.h4("Language", class_name="font-medium text-stone-800 mb-2"),
            rx.el.select(
                rx.el.option("English", value="English"),
                rx.el.option("Tamil", value="Tamil"),
                rx.el.option("Hindi", value="Hindi"),
                value=SettingsState.language,
                on_change=SettingsState.set_language,
                class_name="w-full md:w-1/3 px-4 py-2 border rounded-lg",
            ),
            class_name="py-4",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("database-backup", class_name="h-4 w-4 mr-2"),
                "Backup All Data",
                on_click=SettingsState.backup_data,
                class_name="flex items-center px-4 py-2 bg-stone-800 text-white rounded-lg font-semibold hover:bg-stone-900 transition",
            ),
            class_name="pt-4 border-t border-stone-100",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100",
    )


def settings_page_content() -> rx.Component:
    return rx.el.div(
        profile_section(),
        farm_details_section(),
        preferences_section(),
        class_name="max-w-4xl mx-auto",
    )


def settings_page() -> rx.Component:
    return dashboard_layout(settings_page_content(), "Settings")
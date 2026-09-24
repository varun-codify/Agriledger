"""Settings page with profile, farm details, data management, and integrations."""

import reflex as rx

from app.components.common import (
    BTN_PRIMARY,
    BTN_SECONDARY,
    INPUT_BASE,
    install_app_button,
    segmented_control,
)
from app.components.layout import dashboard_layout
from app.config import config
from app.states.auth_state import AuthState
from app.states.download_state import DownloadState
from app.states.family_state import FamilyState
from app.states.i18n_state import I18nState
from app.states.settings_state import SettingsState
from app.states.ui_state import UIState

# Server-side truth for the Integrations panel: True when a Gemini API key is
# configured (evaluated once at import time, so it reflects the running .env).
GEMINI_ACTIVE = config.gemini.is_configured
# The model name the AI features will try first (the one shown as active).
GEMINI_MODEL_NAME = config.gemini.model


def error_banner(error_var) -> rx.Component:
    return rx.cond(
        error_var != "",
        rx.el.div(
            rx.icon("triangle-alert", class_name="h-4 w-4 mr-2 flex-shrink-0"),
            error_var,
            class_name="flex items-start text-red-600 text-sm bg-red-50 border border-red-200 p-3 rounded-lg mb-4",
        ),
        None,
    )


def profile_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Profile Settings",
            class_name="text-lg font-semibold text-stone-800 mb-4 dark:text-stone-100",
        ),
        error_banner(SettingsState.settings_error),
        rx.el.form(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Full Name",
                        class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                    ),
                    rx.el.input(
                        name="name",
                        default_value=AuthState.user_name,
                        class_name=INPUT_BASE,
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Email Address",
                        class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                    ),
                    rx.el.input(
                        name="email",
                        type="email",
                        default_value=AuthState.user_email,
                        disabled=True,
                        class_name="w-full px-4 py-3 rounded-lg border border-stone-300 bg-stone-50 text-stone-500 dark:bg-stone-800 dark:border-stone-600 dark:text-stone-400",
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
            ),
            rx.el.button(
                "Update Profile",
                type="submit",
                class_name=f"mt-4 px-5 py-2.5 min-h-[40px] {BTN_PRIMARY}",
            ),
            on_submit=SettingsState.update_profile,
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700 mb-6",
    )


def farm_details_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Farm Details",
            class_name="text-lg font-semibold text-stone-800 mb-4 dark:text-stone-100",
        ),
        error_banner(SettingsState.settings_error),
        rx.el.form(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Farm Name",
                        class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                    ),
                    rx.el.input(
                        name="farm_name",
                        default_value=SettingsState.farm_name,
                        class_name=INPUT_BASE,
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Location",
                        class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                    ),
                    rx.el.input(
                        name="farm_location",
                        default_value=SettingsState.farm_location,
                        class_name=INPUT_BASE,
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Farm Size",
                        class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                    ),
                    rx.el.input(
                        name="farm_size",
                        default_value=SettingsState.farm_size,
                        class_name=INPUT_BASE,
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
            ),
            rx.el.button(
                "Save Farm Details",
                type="submit",
                class_name=f"mt-4 px-5 py-2.5 min-h-[40px] {BTN_PRIMARY}",
            ),
            on_submit=SettingsState.update_farm_details,
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700 mb-6",
    )


def family_members_section() -> rx.Component:
    """Family members who share access to this farm."""
    return rx.el.div(
        rx.el.h3(
            "Family Members",
            class_name="text-lg font-semibold text-stone-800 mb-1 dark:text-stone-100",
        ),
        rx.el.p(
            "People you add can log in with their own account and see the same "
            "farm data. If they don't have an account yet, they join the farm "
            "automatically when they sign up.",
            class_name="text-sm text-stone-500 dark:text-stone-400 mb-4",
        ),
        error_banner(FamilyState.family_error),
        # Existing members
        rx.cond(
            FamilyState.members.length() == 0,
            rx.el.div(
                    rx.el.p(
                        "No family members yet. Add the first one below.",
                        class_name="text-sm text-stone-400 py-6 text-center bg-stone-50 rounded-xl mb-4 dark:bg-stone-800 dark:text-stone-400",
                    ),
            ),
            rx.el.div(
                rx.foreach(
                    FamilyState.members,
                    lambda m: rx.el.div(
                        rx.image(
                            src=f"https://api.dicebear.com/9.x/initials/svg?seed={m['name']}",
                            class_name="w-10 h-10 rounded-full border-2 border-stone-200 flex-shrink-0",
                        ),
                        rx.el.div(
                            rx.el.p(
                                m["name"], class_name="font-medium text-stone-800 text-sm dark:text-stone-100"
                            ),
                            rx.el.p(
                                m["email"],
                                rx.cond(
                                    m.get("phone"),
                                    f" · {m['phone']}",
                                    "",
                                ),
                                class_name="text-xs text-stone-500 dark:text-stone-400",
                            ),
                            class_name="flex-1 min-w-0",
                        ),
                        rx.cond(
                            m["status"] == "active",
                            rx.el.span(
                                "Active",
                                class_name="px-2 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700",
                            ),
                            rx.el.span(
                                "Invited",
                                class_name="px-2 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-700",
                            ),
                        ),
                        rx.cond(
                            FamilyState.pending_delete_id == m["id"],
                            rx.el.button(
                                "Confirm?",
                                on_click=lambda: FamilyState.remove_member(m["id"]),
                                class_name="px-3 py-1.5 rounded-md text-xs font-semibold bg-red-600 text-white hover:bg-red-700 transition flex-shrink-0",
                            ),
                            rx.el.button(
                                rx.icon("trash-2", class_name="h-4 w-4"),
                                on_click=lambda: FamilyState.set_pending_delete_id(m["id"]),
                                class_name="p-1.5 rounded-md text-red-400 hover:bg-red-50 hover:text-red-600 transition flex-shrink-0",
                            ),
                        ),
                        class_name="flex items-center gap-3 p-3 bg-stone-50 rounded-xl mb-2 dark:bg-stone-800",
                    ),
                ),
                class_name="mb-4",
            ),
        ),
        # Add-member form
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Name",
                    class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                ),
                rx.el.input(
                    placeholder="e.g., Rani",
                    value=FamilyState.new_member_name,
                    on_change=FamilyState.set_new_member_name,
                    class_name=INPUT_BASE,
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Email",
                    class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                ),
                rx.el.input(
                    type="email",
                    placeholder="e.g., rani@example.com",
                    value=FamilyState.new_member_email,
                    on_change=FamilyState.set_new_member_email,
                    class_name=INPUT_BASE,
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Phone (optional)",
                    class_name="block text-sm font-medium text-stone-700 mb-1 dark:text-stone-300",
                ),
                rx.el.input(
                    type="tel",
                    placeholder="e.g., +91 98765 43210",
                    value=FamilyState.new_member_phone,
                    on_change=FamilyState.set_new_member_phone,
                    class_name=INPUT_BASE,
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
        ),
        rx.el.button(
            rx.icon("user-plus", class_name="h-4 w-4 mr-2"),
            "Add Member",
            on_click=FamilyState.add_member,
            class_name=f"mt-4 flex items-center px-5 py-2.5 min-h-[40px] {BTN_PRIMARY}",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700 mb-6",
    )


def data_management_section() -> rx.Component:
    """Real data export — downloads a JSON backup of every farm collection."""
    return rx.el.div(
        rx.el.h3(
            "Data & Backups",
            class_name="text-lg font-semibold text-stone-800 mb-1 dark:text-stone-100",
        ),
        rx.el.p(
            "Download a full JSON backup of your farm's data — animals, crops, "
            "transactions, milk and coconut sales, breeding cycles, and feed records.",
            class_name="text-sm text-stone-500 dark:text-stone-400 mb-4",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("database-backup", class_name="h-4 w-4 mr-2"),
                rx.cond(
                    SettingsState.is_exporting,
                    "Preparing backup...",
                    "Download JSON Backup",
                ),
                disabled=SettingsState.is_exporting,
                on_click=SettingsState.backup_data,
                class_name=f"flex items-center px-5 py-2.5 min-h-[40px] {BTN_PRIMARY}",
            ),
            rx.el.button(
                rx.icon("package", class_name="h-4 w-4 mr-2"),
                "Download Source ZIP",
                on_click=DownloadState.create_project_zip,
                class_name=f"flex items-center px-5 py-2.5 min-h-[40px] {BTN_SECONDARY} ml-3",
            ),
            class_name="flex flex-wrap gap-3 items-center",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700 mb-6",
    )


def integrations_section() -> rx.Component:
    """Shows integration status for external services (server-side truth)."""
    return rx.el.div(
        rx.el.h3(
            "Integrations",
            class_name="text-lg font-semibold text-stone-800 mb-4 dark:text-stone-100",
        ),
        rx.el.div(
            # Gemini
            rx.el.div(
                rx.icon("brain-circuit", class_name="h-5 w-5 text-stone-500 dark:text-stone-400"),
                rx.el.div(
                    rx.el.p("Gemini (AI + Bill Scanning)", class_name="font-medium text-stone-700 dark:text-stone-200"),
                    rx.el.p("Powers AI recommendations, the chatbot, and milk-bill photo OCR (fat %, SNF %, litres, amount).", class_name="text-xs text-stone-500 dark:text-stone-400"),
                ),
                (
                    rx.el.span(
                        f"Active · {GEMINI_MODEL_NAME}",
                        class_name="text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-700",
                    )
                    if GEMINI_ACTIVE
                    else rx.el.span(
                        "Set GEMINI_API_KEY in .env & restart",
                        class_name="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300",
                    )
                ),
                class_name="flex items-center justify-between py-3 border-b border-stone-100 dark:border-stone-700",
            ),
            # Weather
            rx.el.div(
                rx.icon("cloud-sun", class_name="h-5 w-5 text-stone-500 dark:text-stone-400"),
                rx.el.div(
                    rx.el.p("Weather (Open-Meteo)", class_name="font-medium text-stone-700 dark:text-stone-200"),
                    rx.el.p("Live forecast and farming suggestions. Free, no key needed.", class_name="text-xs text-stone-500 dark:text-stone-400"),
                ),
                rx.el.span(
                    "Active",
                    class_name="text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-700",
                ),
                class_name="flex items-center justify-between py-3 border-b border-stone-100 dark:border-stone-700",
            ),
            # API
            rx.el.div(
                rx.icon("braces", class_name="h-5 w-5 text-stone-500 dark:text-stone-400"),
                rx.el.div(
                    rx.el.p("REST API", class_name="font-medium text-stone-700 dark:text-stone-200"),
                    rx.el.p("Bearer-authenticated API served from the same app: /docs, /health.", class_name="text-xs text-stone-500 dark:text-stone-400"),
                ),
                rx.el.span(
                    "Same origin",
                    class_name="text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-700",
                ),
                class_name="flex items-center justify-between py-3 border-b border-stone-100 dark:border-stone-700",
            ),
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700",
    )


def install_section() -> rx.Component:
    """Install the app on this device (uses the browser install prompt)."""
    return rx.cond(
        UIState.install_prompt_available,
        rx.el.div(
            rx.el.h3(
                "Install App",
                class_name="text-lg font-semibold text-stone-800 mb-4 dark:text-stone-100",
            ),
            rx.el.p(
                "Install AgriLedger on this device for a native-app experience — ",
                "fullscreen, with its own icon on your home screen.",
                class_name="text-sm text-stone-500 dark:text-stone-400 mb-4",
            ),
            install_app_button(),
            rx.el.p(
                "Tip: on iOS, use your browser's Share → ",
                rx.el.span("Add to Home Screen", class_name="font-medium"),
                ".",
                class_name="text-xs text-stone-400 mt-3",
            ),
            class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700 mb-6",
        ),
        None,
    )


def preferences_section() -> rx.Component:
    """Theme + language preferences (dark mode toggle and language switcher)."""
    languages = [("English", "English"), ("Tamil", "தமிழ்"), ("Hindi", "हिन्दी")]
    return rx.el.div(
        rx.el.h3(
            "Preferences",
            class_name="text-lg font-semibold text-stone-800 mb-4 dark:text-stone-100",
        ),
        # Dark mode
        rx.el.div(
            rx.el.div(
                rx.icon("moon", class_name="h-5 w-5 text-stone-500 dark:text-stone-400"),
                rx.el.div(
                    rx.el.p(
                        "Dark Mode",
                        class_name="font-medium text-stone-700 dark:text-stone-200",
                    ),
                    rx.el.p(
                        "Easier on the eyes at night. Saved on this device.",
                        class_name="text-xs text-stone-500 dark:text-stone-400",
                    ),
                ),
                class_name="flex items-center gap-3 flex-1",
            ),
            rx.el.button(
                rx.el.div(
                    rx.el.div(
                        class_name=rx.cond(
                            UIState.dark_mode,
                            "h-5 w-5 rounded-full bg-white shadow transform translate-x-5 transition-transform duration-200",
                            "h-5 w-5 rounded-full bg-white shadow transform translate-x-0 transition-transform duration-200",
                        ),
                    ),
                    class_name=rx.cond(
                        UIState.dark_mode,
                        "w-11 h-6 bg-emerald-500 rounded-full p-0.5 transition-colors",
                        "w-11 h-6 bg-stone-300 rounded-full p-0.5 transition-colors",
                    ),
                ),
                on_click=UIState.toggle_theme,
                role="switch",
                aria_checked=UIState.dark_mode,
                aria_label="Toggle dark mode",
                class_name="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 rounded-full",
            ),
            class_name="flex items-center justify-between py-3 border-b border-stone-100 dark:border-stone-700",
        ),
        # Language
        rx.el.div(
            rx.el.div(
                rx.icon("languages", class_name="h-5 w-5 text-stone-500 dark:text-stone-400"),
                rx.el.div(
                    rx.el.p(
                        "Language",
                        class_name="font-medium text-stone-700 dark:text-stone-200",
                    ),
                    rx.el.p(
                        "Navigation and dashboard labels.",
                        class_name="text-xs text-stone-500 dark:text-stone-400",
                    ),
                ),
                class_name="flex items-center gap-3 flex-1",
            ),
            rx.el.div(
                rx.foreach(
                    languages,
                    lambda opt: rx.el.button(
                        opt[1],
                        on_click=lambda o=opt: I18nState.set_language(o[0]),
                        class_name=rx.cond(
                            I18nState.language == opt[0],
                            "px-3 py-1.5 rounded-lg text-sm font-semibold bg-emerald-500 text-white transition-all active:scale-95",
                            "px-3 py-1.5 rounded-lg text-sm font-semibold text-stone-600 dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-stone-700 transition-all active:scale-95",
                        ),
                    ),
                ),
                class_name="flex items-center gap-1.5",
            ),
            class_name="flex items-center justify-between py-3",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-100 dark:bg-stone-900 dark:border-stone-700 mb-6",
    )


def settings_page_content() -> rx.Component:
    return rx.el.div(
        segmented_control(
            SettingsState.active_tab,
            [
                ("account", "Account", "user-round"),
                ("preferences", "Preferences", "settings-2"),
                ("people", "People", "users"),
                ("data", "Data", "database"),
            ],
            SettingsState.set_active_tab,
            container_class="mb-6 flex-wrap",
        ),
        rx.cond(
            SettingsState.active_tab == "account",
            rx.el.div(
                profile_section(),
                farm_details_section(),
            ),
            rx.cond(
                SettingsState.active_tab == "preferences",
                rx.el.div(
                    preferences_section(),
                    install_section(),
                ),
                rx.cond(
                    SettingsState.active_tab == "people",
                    family_members_section(),
                    rx.el.div(
                        data_management_section(),
                        integrations_section(),
                    ),
                ),
            ),
        ),
        class_name="max-w-4xl mx-auto",
    )


def settings_page() -> rx.Component:
    return dashboard_layout(settings_page_content(), "Settings")

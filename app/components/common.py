"""Small shared UI building blocks used across pages."""

import reflex as rx

from app.states.ui_state import UIState



def install_app_button(compact: bool = False) -> rx.Component:
    """An "Install App" button that shows only when a PWA install is possible.

    The browser captures a ``beforeinstallprompt`` event (see ``app.py`` head
    scripts) and stores it on ``window.__agriledgerDeferredPrompt``;
    ``UIState.install_app`` calls ``prompt()`` on it. The button disappears once
    installed or when the prompt is not available.

    Args:
        compact: Render as a small icon-only chip (for the dashboard header).
    """
    if compact:
        button = rx.el.button(
            rx.icon("download", class_name="h-4 w-4"),
            on_click=UIState.install_app,
            title="Install AgriLedger on this device",
            aria_label="Install AgriLedger as an app",
            class_name="flex items-center gap-1.5 rounded-lg p-2 text-emerald-600 hover:bg-emerald-50 transition-colors",
        )
    else:
        button = rx.el.button(
            rx.icon("download", class_name="h-4 w-4 flex-shrink-0"),
            rx.el.span("Install App", class_name="truncate"),
            on_click=UIState.install_app,
            title="Install AgriLedger on this device",
            aria_label="Install AgriLedger as an app",
            class_name="flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2.5 bg-emerald-500 text-white font-semibold hover:bg-emerald-600 transition-all",
        )
    return rx.cond(
        UIState.install_prompt_available,
        button,
        None,
    )


def segmented_control(
    active: rx.Var,
    options: list[tuple[str, str, str]],
    on_change,
    container_class: str = "",
) -> rx.Component:
    """A pill-style segmented control (Cards/Table toggles, tab bars).

    Args:
        active: The currently selected value, as a Var.
        options: ``(value, label, icon)`` triples.
        on_change: An event handler (or callable returning an EventSpec) that
            receives the selected value.
        container_class: Extra classes appended to the container.
    """
    buttons = []
    for value, label, icon in options:
        buttons.append(
            rx.el.button(
                (
                    rx.icon(icon, class_name="h-4 w-4 mr-1.5")
                    if icon
                    else None
                ),
                rx.el.span(label, class_name="whitespace-nowrap"),
                # Build the event spec eagerly: ``on_change`` may be an event
                # handler (``State.set_tab``) or a callable returning specs.
                on_click=on_change(value),
                class_name=rx.cond(
                    active == value,
                    "flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-emerald-500 text-white transition-all",
                    "flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-white text-stone-600 border hover:bg-stone-50 transition-all",
                ),
            )
        )
    return rx.el.div(
        buttons,
        class_name=f"flex items-center gap-2 bg-white p-1 rounded-xl border border-stone-200 {container_class}".strip(),
    )

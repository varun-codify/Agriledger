"""Small shared UI building blocks used across pages."""

import reflex as rx

from app.states.ui_state import UIState

# ── Button recipes ────────────────────────────────────────────────────
# One source of truth so every action gets hover / press / focus feedback.

BTN_BASE = "font-semibold rounded-lg transition-all active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/50 disabled:opacity-60 disabled:pointer-events-none"

BTN_PRIMARY = f"{BTN_BASE} bg-emerald-500 text-white shadow-sm hover:bg-emerald-600 hover:shadow-md"

BTN_SECONDARY = f"{BTN_BASE} bg-stone-200 text-stone-800 hover:bg-stone-300 dark:bg-stone-700 dark:text-stone-100 dark:hover:bg-stone-600"

BTN_GHOST = f"{BTN_BASE} bg-transparent text-stone-600 hover:bg-stone-100 dark:text-stone-300 dark:hover:bg-stone-800"

BTN_DANGER = f"{BTN_BASE} bg-red-500 text-white hover:bg-red-600"

# Standard input field classes (focus ring + transition everywhere).
INPUT_BASE = "w-full px-4 py-3 rounded-lg border border-stone-300 bg-white text-stone-800 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition dark:bg-stone-800 dark:border-stone-600 dark:text-stone-100"
INPUT_ERROR = "w-full px-4 py-3 rounded-lg border-2 border-red-400 bg-red-50/50 text-stone-800 focus:ring-2 focus:ring-red-400 focus:border-transparent transition al-shake dark:bg-red-950/30 dark:text-stone-100"


def spinner(size: str = "h-4 w-4") -> rx.Component:
    """A loading spinner matching the button/inline loading pattern."""
    return rx.icon("loader-circle", class_name=f"{size} animate-spin")


def field_error(message: rx.Var | str) -> rx.Component:
    """Inline red validation message shown under a form field."""
    return rx.el.p(
        message,
        class_name="text-red-500 text-sm mt-1 flex items-center gap-1 al-fade-up",
    )


def empty_state(
    icon: str,
    title: str,
    description: str = "",
    action: rx.Component | None = None,
) -> rx.Component:
    """A friendly empty state block (icon + title + optional description/CTA)."""
    return rx.el.div(
        rx.icon(icon, class_name="h-12 w-12 text-stone-300 mx-auto dark:text-stone-600"),
        rx.el.p(title, class_name="text-stone-700 font-semibold mt-3 dark:text-stone-200"),
        rx.cond(
            description != "",
            rx.el.p(
                description,
                class_name="text-sm text-stone-500 dark:text-stone-400 mt-1 dark:text-stone-400",
            ),
            None,
        ),
        rx.cond(action is not None, action, None),
        class_name="py-12 text-center al-fade-up",
    )


def modal_shell(
    content: rx.Component,
    open_var: rx.Var[bool],
    on_close,
    max_width: str = "max-w-lg",
) -> rx.Component:
    """Centered modal with animated enter (scale + fade) and blurred backdrop.

    Exit is instant (Reflex ``rx.cond`` unmounts immediately); enter always
    plays via the ``al-modal-in`` CSS animation.
    """
    return rx.cond(
        open_var,
        rx.el.div(
            rx.el.div(
                on_click=on_close,
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 al-fade-in",
            ),
            rx.el.div(
                content,
                class_name=f"al-modal-in bg-white dark:bg-stone-900 p-8 rounded-2xl shadow-xl w-full {max_width} z-50 max-h-[90vh] overflow-y-auto border border-stone-100 dark:border-stone-700",
            ),
            class_name="fixed inset-0 flex items-center justify-center p-4 z-50",
        ),
    )


def loading_button(
    label: str,
    is_loading: rx.Var[bool],
    on_click=None,
    button_class: str = BTN_PRIMARY,
    type_: str = "button",
    icon_name: str | None = None,
) -> rx.Component:
    """A primary button that swaps its label for a spinner while loading."""
    children = [
        rx.cond(
            is_loading,
            spinner(),
            rx.el.span(
                rx.fragment(
                    rx.icon(icon_name, class_name="h-4 w-4 mr-2")
                    if icon_name
                    else rx.fragment()
                ),
                label,
                class_name="inline-flex items-center",
            ),
        )
    ]
    if on_click is not None:
        return rx.el.button(
            *children,
            on_click=on_click,
            type=type_,
            disabled=is_loading,
            class_name=button_class,
        )
    return rx.el.button(
        *children, type=type_, disabled=is_loading, class_name=button_class
    )


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
            class_name="flex items-center gap-1.5 rounded-lg p-2 text-emerald-600 hover:bg-emerald-50 transition-colors dark:hover:bg-emerald-950",
        )
    else:
        button = rx.el.button(
            rx.icon("download", class_name="h-4 w-4 flex-shrink-0"),
            rx.el.span("Install App", class_name="truncate"),
            on_click=UIState.install_app,
            title="Install AgriLedger on this device",
            aria_label="Install AgriLedger as an app",
            class_name=f"flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2.5 {BTN_PRIMARY}",
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
                    "flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-white text-stone-600 border hover:bg-stone-50 dark:bg-stone-800 dark:text-stone-300 dark:border-stone-600 dark:hover:bg-stone-700 transition-all active:scale-95",
                ),
            )
        )
    return rx.el.div(
        buttons,
        class_name=f"flex items-center gap-2 bg-white p-1 rounded-xl border border-stone-200 dark:bg-stone-900 dark:border-stone-700 {container_class}".strip(),
    )

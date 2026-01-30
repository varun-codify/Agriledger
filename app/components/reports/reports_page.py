import reflex as rx

def reports_page() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Reports", class_name="text-2xl font-bold mb-4"),
        rx.el.p("Reports functionality coming soon.", class_name="text-stone-600"),
        class_name="p-8 bg-white rounded-2xl shadow border border-stone-100 max-w-3xl mx-auto mt-8"
    )

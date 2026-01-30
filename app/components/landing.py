import reflex as rx
from app.states.download_state import DownloadState


def hero_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            # Skip to main content link for accessibility
            rx.el.a(
                "Skip to main content",
                href="#features",
                class_name="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-emerald-600 focus:text-white focus:rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-400",
            ),
            # Hero content container
            rx.el.div(
                # Badge or tagline
                rx.el.div(
                    rx.icon("sparkles", class_name="h-4 w-4 mr-2 text-emerald-600", aria_hidden="true"),
                    "Smart Farm Management Platform",
                    class_name="inline-flex items-center px-4 py-2 rounded-full bg-emerald-50 text-emerald-700 font-medium text-sm mb-6 border border-emerald-200",
                    role="note",
                    aria_label="Platform category badge",
                ),
                rx.el.h1(
                    "Modern Financial Tools for the ",
                    rx.el.span(
                        "Modern Farmer",
                        class_name="bg-gradient-to-r from-emerald-600 to-emerald-400 bg-clip-text text-transparent",
                    ),
                    class_name="text-4xl md:text-6xl lg:text-7xl font-bold text-stone-800 text-center leading-tight",
                    id="main-heading",
                ),
                rx.el.p(
                    "Track expenses, manage cattle, and gain smart insights to boost your farm's profitability. All in one simple, beautiful platform.",
                    class_name="mt-6 max-w-2xl mx-auto text-center text-lg md:text-xl text-stone-600 leading-relaxed",
                    role="doc-subtitle",
                ),
                # CTA Buttons with proper accessibility
                rx.el.div(
                    rx.el.a(
                        "Get Started Free",
                        rx.icon("arrow-right", class_name="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform", aria_hidden="true"),
                        href="/register",
                        class_name="group inline-flex items-center bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-emerald-600 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 focus:outline-none focus:ring-4 focus:ring-emerald-300",
                        aria_label="Sign up for free account",
                        role="button",
                    ),
                    rx.el.a(
                        rx.icon("play-circle", class_name="h-5 w-5 mr-2", aria_hidden="true"),
                        "Watch Demo",
                        href="#features",
                        class_name="inline-flex items-center bg-white text-stone-700 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-stone-50 transition-all border-2 border-stone-200 shadow-md hover:shadow-lg focus:outline-none focus:ring-4 focus:ring-stone-300",
                        aria_label="Watch product demo video",
                    ),
                    class_name="mt-10 flex flex-wrap justify-center gap-4",
                    role="group",
                    aria_label="Call to action buttons",
                ),
                # Download button (secondary)
                rx.el.div(
                    rx.el.button(
                        rx.icon("download", class_name="h-4 w-4 mr-2", aria_hidden="true"),
                        "Download Project Files",
                        on_click=DownloadState.create_project_zip,
                        class_name="inline-flex items-center text-stone-600 hover:text-stone-800 font-medium text-sm transition-colors underline-offset-4 hover:underline focus:outline-none focus:ring-2 focus:ring-stone-400 rounded px-2 py-1",
                        aria_label="Download project source files",
                    ),
                    class_name="mt-6 text-center",
                ),
                class_name="max-w-5xl mx-auto flex flex-col items-center",
            ),
            # Dashboard Preview with proper accessibility
            rx.el.div(
                rx.el.figure(
                    rx.image(
                        src="/dashboard-preview.png",
                        alt="AgriLedger dashboard interface showing income statistics of $254,800, expense tracking at $145,320, net profit of $109,480, animal count of 1,250, milk production trends chart, expense categories pie chart, recent transactions table, current weather widget displaying 78°F sunny conditions, and upcoming tasks calendar for June 2024",
                        class_name="rounded-2xl w-full shadow-2xl ring-1 ring-stone-900/10",
                        loading="eager",
                        style={"aspectRatio": "16/9", "objectFit": "cover"},
                    ),
                    rx.el.figcaption(
                        "Dashboard preview showcasing AgriLedger's comprehensive farm management features",
                        class_name="sr-only",
                    ),
                    class_name="relative",
                ),
                class_name="mt-20 max-w-6xl mx-auto px-4",
                role="region",
                aria_label="Product preview",
            ),
            class_name="relative max-w-7xl mx-auto px-4",
        ),
        # Decorative background elements
        style={
            "background": "linear-gradient(180deg, #fef6e8 0%, #f5f5f4 100%)",
            "position": "relative",
        },
        class_name="py-24 md:py-32 px-4 overflow-hidden",
        aria_labelledby="main-heading",
    )


def feature_card(icon: str, title: str, description: str) -> rx.Component:
    return rx.el.article(
        # Icon container with gradient background
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-white", aria_hidden="true"),
            class_name="h-12 w-12 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center mb-4 shadow-md group-hover:shadow-lg transition-shadow",
            role="img",
            aria_label=f"{title} icon",
        ),
        rx.el.h3(title, class_name="text-xl font-bold text-stone-800 mb-2"),
        rx.el.p(description, class_name="text-stone-600 leading-relaxed"),
        class_name="group bg-white p-8 rounded-2xl shadow-md border border-stone-100 hover:shadow-xl hover:-translate-y-2 focus-within:ring-4 focus-within:ring-emerald-300 transition-all duration-300 tabindex-0",
        tabindex="0",
        role="region",
        aria_label=f"{title} feature",
    )


def features_section() -> rx.Component:
    features = [
        {
            "icon": "receipt",
            "title": "Expense Tracking",
            "description": "Log every cost from feed to fertilizer with ease.",
        },
        {
            "icon": "git-fork",
            "title": "Cattle Management",
            "description": "Track individual animal health, milking, and profitability.",
        },
        {
            "icon": "sprout",
            "title": "Crop Management",
            "description": "Monitor crop cycles, yields, and input costs per field.",
        },
        {
            "icon": "bar-chart-3",
            "title": "Smart Analytics",
            "description": "Visualize your farm's financial health with intuitive charts.",
        },
        {
            "icon": "file-text",
            "title": "Detailed Reports",
            "description": "Generate PDF/Excel reports for accounting and planning.",
        },
        {
            "icon": "brain-circuit",
            "title": "AI Insights",
            "description": "Get smart suggestions to optimize spending and increase yield.",
        },
    ]
    return rx.el.section(
        rx.el.div(
            # Section header
            rx.el.header(
                rx.el.div(
                    "Features",
                    class_name="inline-block px-4 py-1.5 rounded-full bg-emerald-50 text-emerald-700 font-semibold text-sm mb-4 border border-emerald-200",
                    role="note",
                ),
                rx.el.h2(
                    "Everything Your Farm Needs",
                    class_name="text-3xl md:text-5xl font-bold text-stone-800 text-center",
                    id="features-heading",
                ),
                rx.el.p(
                    "One comprehensive platform to manage your entire agricultural business.",
                    class_name="mt-4 text-lg md:text-xl text-stone-600 text-center max-w-2xl mx-auto",
                ),
                class_name="text-center",
            ),
            # Feature cards grid
            rx.el.div(
                rx.foreach(
                    features,
                    lambda f: feature_card(f["icon"], f["title"], f["description"]),
                ),
                class_name="mt-16 grid md:grid-cols-2 lg:grid-cols-3 gap-8",
                role="list",
                aria_label="Product features",
            ),
            id="features",
            class_name="max-w-7xl mx-auto px-4",
        ),
        class_name="py-24 md:py-32 bg-gradient-to-b from-stone-50 to-white",
        aria_labelledby="features-heading",
    )


def about_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.article(
                # Section badge
                rx.el.div(
                    "About AgriLedger",
                    class_name="inline-block px-4 py-1.5 rounded-full bg-emerald-50 text-emerald-700 font-semibold text-sm mb-6 border border-emerald-200",
                    role="note",
                ),
                rx.el.h2(
                    "Built for the Future of Farming",
                    class_name="text-3xl md:text-5xl font-bold text-stone-800 mb-6",
                    id="about-heading",
                ),
                rx.el.p(
                    "AgriLedger was born from a simple idea: farmers deserve the same powerful, easy-to-use financial tools as any other modern business. We combine cutting-edge technology with a deep understanding of agricultural challenges to provide a platform that simplifies your finances, so you can focus on what you do best—farming.",
                    class_name="text-lg md:text-xl text-stone-600 leading-relaxed",
                ),
                # Key stats or benefits
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            "10,000+",
                            class_name="text-3xl md:text-4xl font-bold text-emerald-600",
                            aria_label="More than 10,000",
                        ),
                        rx.el.div("Farmers Served", class_name="text-stone-600 mt-1"),
                        class_name="text-center",
                        role="group",
                        aria_label="Farmers served statistic",
                    ),
                    rx.el.div(
                        rx.el.div(
                            "99.9%",
                            class_name="text-3xl md:text-4xl font-bold text-emerald-600",
                            aria_label="99.9 percent",
                        ),
                        rx.el.div("Uptime", class_name="text-stone-600 mt-1"),
                        class_name="text-center",
                        role="group",
                        aria_label="Uptime reliability statistic",
                    ),
                    rx.el.div(
                        rx.el.div(
                            "24/7",
                            class_name="text-3xl md:text-4xl font-bold text-emerald-600",
                            aria_label="24 hours, 7 days",
                        ),
                        rx.el.div("Support", class_name="text-stone-600 mt-1"),
                        class_name="text-center",
                        role="group",
                        aria_label="Customer support availability",
                    ),
                    class_name="mt-12 grid grid-cols-3 gap-8",
                    role="list",
                    aria_label="Company statistics",
                ),
                id="about",
                class_name="max-w-4xl mx-auto text-center px-4",
            ),
        ),
        class_name="py-24 md:py-32 bg-white",
        aria_labelledby="about-heading",
    )


def pricing_card(
    plan: str, price: str, features: list, popular: bool = False
) -> rx.Component:
    return rx.el.article(
        # Popular badge
        rx.cond(
            popular,
            rx.el.div(
                rx.icon("star", class_name="h-3 w-3 mr-1", aria_hidden="true"),
                "Most Popular",
                class_name="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-4 py-1 rounded-full text-xs font-semibold flex items-center shadow-md",
                role="status",
                aria_label="Most popular plan",
            ),
            None,
        ),
        rx.el.h3(plan, class_name="text-2xl font-bold text-stone-800"),
        rx.el.div(
            rx.el.span(
                f"${price}",
                class_name="text-5xl font-bold text-stone-800",
                aria_label=f"{price} dollars",
            ),
            rx.el.span("/month", class_name="text-stone-500 text-lg ml-2"),
            class_name="mt-6 flex items-baseline",
        ),
        rx.el.ul(
            rx.foreach(
                features,
                lambda feature: rx.el.li(
                    rx.el.div(
                        rx.icon("check", class_name="h-5 w-5 text-emerald-500", aria_hidden="true"),
                        class_name="flex-shrink-0 h-6 w-6 rounded-full bg-emerald-50 flex items-center justify-center",
                        role="img",
                        aria_label="Included feature",
                    ),
                    rx.el.span(feature, class_name="text-stone-600"),
                    class_name="flex items-center gap-3",
                ),
            ),
            class_name="mt-8 space-y-4",
            role="list",
            aria_label=f"{plan} features",
        ),
        rx.el.a(
            "Get Started",
            href="/register",
            class_name=rx.cond(
                popular,
                "mt-8 w-full block text-center bg-gradient-to-r from-emerald-500 to-emerald-600 text-white px-6 py-3.5 rounded-xl font-semibold hover:from-emerald-600 hover:to-emerald-700 transition-all shadow-md hover:shadow-lg focus:outline-none focus:ring-4 focus:ring-emerald-300",
                "mt-8 w-full block text-center bg-white text-emerald-600 px-6 py-3.5 rounded-xl font-semibold hover:bg-emerald-50 border-2 border-emerald-500 transition-all focus:outline-none focus:ring-4 focus:ring-emerald-300",
            ),
            aria_label=f"Get started with {plan} plan",
            role="button",
        ),
        class_name=rx.cond(
            popular,
            "relative bg-white p-8 rounded-2xl shadow-xl border-2 border-emerald-500 hover:shadow-2xl transition-shadow focus-within:ring-4 focus-within:ring-emerald-300",
            "relative bg-white p-8 rounded-2xl shadow-md border border-stone-200 hover:shadow-lg transition-shadow focus-within:ring-4 focus-within:ring-emerald-300",
        ),
        role="region",
        aria_label=f"{plan} pricing plan",
    )


def pricing_section() -> rx.Component:
    hobby_features = ["Up to 50 cattle", "Basic Expense Tracking", "Community Support"]
    pro_features = [
        "Unlimited Cattle & Crops",
        "Advanced Analytics",
        "PDF & Excel Reports",
        "AI-Powered Insights",
        "Priority Support",
    ]
    return rx.el.section(
        rx.el.div(
            # Section header
            rx.el.header(
                rx.el.div(
                    "Pricing",
                    class_name="inline-block px-4 py-1.5 rounded-full bg-emerald-50 text-emerald-700 font-semibold text-sm mb-4 border border-emerald-200",
                    role="note",
                ),
                rx.el.h2(
                    "Simple, Transparent Pricing",
                    class_name="text-3xl md:text-5xl font-bold text-stone-800 text-center",
                    id="pricing-heading",
                ),
                rx.el.p(
                    "Choose the plan that's right for your farm. No hidden fees.",
                    class_name="mt-4 text-lg md:text-xl text-stone-600 text-center max-w-2xl mx-auto",
                ),
                class_name="text-center",
            ),
            # Pricing cards
            rx.el.div(
                pricing_card("Hobby Farmer", "12", hobby_features),
                pricing_card("Pro Farmer", "29", pro_features, popular=True),
                class_name="mt-16 grid md:grid-cols-2 gap-8 max-w-4xl mx-auto px-4",
                role="list",
                aria_label="Pricing plans",
            ),
            id="pricing",
            class_name="max-w-7xl mx-auto",
        ),
        class_name="py-24 md:py-32 bg-gradient-to-b from-white to-stone-50",
        aria_labelledby="pricing-heading",
    )


def footer_section() -> rx.Component:
    """Footer with links and copyright info."""
    return rx.el.footer(
        rx.el.div(
            # Top section with links
            rx.el.nav(
                # Brand column
                rx.el.div(
                    rx.el.div(
                        rx.icon("leaf", class_name="h-8 w-8 text-emerald-500", aria_hidden="true"),
                        rx.el.span(
                            "AgriLedger", class_name="text-xl font-bold text-stone-800"
                        ),
                        class_name="flex items-center gap-2 mb-4",
                    ),
                    rx.el.p(
                        "Modern farm management tools for the modern farmer.",
                        class_name="text-stone-600 max-w-xs",
                    ),
                ),
                # Quick Links
                rx.el.div(
                    rx.el.h4(
                        "Quick Links", class_name="font-bold text-stone-800 mb-4"
                    ),
                    rx.el.ul(
                        rx.el.li(
                            rx.el.a(
                                "Features",
                                href="#features",
                                class_name="text-stone-600 hover:text-emerald-600 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-1",
                                aria_label="Navigate to Features section",
                            )
                        ),
                        rx.el.li(
                            rx.el.a(
                                "About",
                                href="#about",
                                class_name="text-stone-600 hover:text-emerald-600 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-1",
                                aria_label="Navigate to About section",
                            )
                        ),
                        rx.el.li(
                            rx.el.a(
                                "Pricing",
                                href="#pricing",
                                class_name="text-stone-600 hover:text-emerald-600 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-1",
                                aria_label="Navigate to Pricing section",
                            )
                        ),
                        class_name="space-y-2",
                        role="list",
                    ),
                ),
                # Legal
                rx.el.div(
                    rx.el.h4("Legal", class_name="font-bold text-stone-800 mb-4"),
                    rx.el.ul(
                        rx.el.li(
                            rx.el.a(
                                "Privacy Policy",
                                href="#",
                                class_name="text-stone-600 hover:text-emerald-600 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-1",
                            )
                        ),
                        rx.el.li(
                            rx.el.a(
                                "Terms of Service",
                                href="#",
                                class_name="text-stone-600 hover:text-emerald-600 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded px-1",
                            )
                        ),
                        class_name="space-y-2",
                        role="list",
                    ),
                ),
                # Get Started
                rx.el.div(
                    rx.el.h4("Get Started", class_name="font-bold text-stone-800 mb-4"),
                    rx.el.a(
                        "Sign Up Now",
                        href="/register",
                        class_name="inline-block bg-emerald-500 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-emerald-600 transition-all shadow-sm focus:outline-none focus:ring-4 focus:ring-emerald-300",
                        aria_label="Sign up for AgriLedger account",
                        role="button",
                    ),
                ),
                class_name="grid grid-cols-2 md:grid-cols-4 gap-8 pb-8 border-b border-stone-200",
                aria_label="Footer navigation",
            ),
            # Bottom section with copyright
            rx.el.div(
                rx.el.p(
                    f"© {rx.State.router.page.host} 2024 AgriLedger. All rights reserved.",
                    class_name="text-stone-600 text-sm",
                    role="contentinfo",
                ),
                rx.el.nav(
                    rx.el.a(
                        rx.icon("twitter", class_name="h-5 w-5"),
                        href="#",
                        class_name="text-stone-600 hover:text-emerald-600 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded p-1",
                        aria_label="Visit our Twitter page",
                    ),
                    rx.el.a(
                        rx.icon("facebook", class_name="h-5 w-5"),
                        href="#",
                        class_name="text-stone-600 hover:text-emerald-600 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded p-1",
                        aria_label="Visit our Facebook page",
                    ),
                    rx.el.a(
                        rx.icon("linkedin", class_name="h-5 w-5"),
                        href="#",
                        class_name="text-stone-600 hover:text-emerald-600 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded p-1",
                        aria_label="Visit our LinkedIn page",
                    ),
                    class_name="flex items-center gap-4",
                    aria_label="Social media links",
                ),
                class_name="pt-8 flex flex-col md:flex-row justify-between items-center gap-4",
            ),
            class_name="max-w-7xl mx-auto px-4",
        ),
        class_name="py-16 bg-stone-50 border-t border-stone-200",
        role="contentinfo",
        aria_label="Site footer",
    )


def landing_page() -> rx.Component:
    """The main landing page component."""
    return rx.el.div(
        hero_section(),
        features_section(),
        about_section(),
        pricing_section(),
        footer_section(),
    )
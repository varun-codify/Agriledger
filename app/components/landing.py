import reflex as rx

# ── Unsplash image URLs (free to use, direct links) ───────────────────
# These are stable Unsplash photo URLs that work without API keys.

IMG_HERO = "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1920&q=80"
IMG_FARMER_PLOUGHING = "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80"
IMG_CATTLE_FIELD = "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=800&q=80"
IMG_MILKING = "https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?w=800&q=80"
IMG_HARVEST = "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800&q=80"
IMG_FARMER_PORTRAIT = "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400&q=80"
IMG_FARMER_WOMAN = "https://images.unsplash.com/photo-1589923188900-85dae523342b?w=400&q=80"
IMG_FARMER_OLD = "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?w=400&q=80"
IMG_GREEN_FIELD = "https://images.unsplash.com/photo-1500595046743-cd271d694d30?w=1200&q=80"
IMG_COW_CLOSE = "https://images.unsplash.com/photo-1596733430284-f7437764b1a9?w=800&q=80"
IMG_RICE_FIELD = "https://images.unsplash.com/photo-1536657464919-89233fa9d0bf?w=1200&q=80"
IMG_FARMER_TABLET = "https://images.unsplash.com/photo-1586771107445-b3e04b584c24?w=800&q=80"
IMG_SUNRISE_FARM = "https://images.unsplash.com/photo-1473973916745-82d5a4d38f1a?w=1200&q=80"


# ── Reusable helpers ──────────────────────────────────────────────────


def _section_badge(text: str) -> rx.Component:
    return rx.el.div(
        text,
        class_name="inline-block px-4 py-1.5 rounded-full bg-emerald-50 text-emerald-700 font-semibold text-sm mb-4 border border-emerald-200",
        role="note",
    )


def _section_heading(title: str, subtitle: str, id_: str = "") -> rx.Component:
    return rx.el.header(
        _section_badge(title.split()[0] if title.split() else title),
        rx.el.h2(
            title,
            class_name="text-3xl md:text-5xl font-bold text-stone-800 text-center",
            id=id_ if id_ else None,
        ),
        rx.el.p(
            subtitle,
            class_name="mt-4 text-lg md:text-xl text-stone-600 text-center max-w-2xl mx-auto",
        ),
        class_name="text-center",
    )


# ══════════════════════════════════════════════════════════════════════
#  HERO SECTION
# ══════════════════════════════════════════════════════════════════════


def hero_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            # Skip to main content link for accessibility
            rx.el.a(
                "Skip to main content",
                href="#features",
                class_name="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-emerald-600 focus:text-white focus:rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-400",
            ),
            # ── Hero image background ──
            rx.el.div(
                rx.image(
                    src=IMG_HERO,
                    alt="Golden sunrise over a lush green farm field with a farmer walking through the crops",
                    class_name="absolute inset-0 w-full h-full object-cover",
                    loading="eager",
                ),
                # Dark gradient overlay for text readability
                rx.el.div(
                    class_name="absolute inset-0",
                    style={
                        "background": "linear-gradient(135deg, rgba(6,78,59,0.85) 0%, rgba(16,163,127,0.7) 40%, rgba(5,150,105,0.5) 100%)",
                    },
                ),
                # Decorative pattern overlay
                rx.el.div(
                    class_name="absolute inset-0 opacity-10",
                    style={
                        "backgroundImage": "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
                    },
                ),
                # Hero content
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "sparkles",
                                class_name="h-4 w-4 mr-2 text-emerald-200",
                                aria_hidden="true",
                            ),
                            "🌾 Trusted by 10,000+ Farmers Across India",
                            class_name="inline-flex items-center px-4 py-2 rounded-full bg-white/15 backdrop-blur-sm text-emerald-100 font-medium text-sm mb-6 border border-white/20",
                            role="note",
                            aria_label="Platform trust badge",
                        ),
                        rx.el.h1(
                            [
                                "From Soil to ",
                                rx.el.span(
                                    "Success",
                                    class_name="bg-gradient-to-r from-emerald-300 to-yellow-300 bg-clip-text text-transparent",
                                ),
                                ",",
                                rx.el.br(),
                                rx.el.span(
                                    "Manage Your Farm",
                                    class_name="text-white",
                                ),
                                " with Confidence.",
                            ],
                            class_name="text-4xl md:text-6xl lg:text-7xl font-bold text-white text-center leading-tight",
                            id="main-heading",
                        ),
                        rx.el.p(
                            "Track expenses, manage cattle, monitor crops, and unlock AI-powered insights — all from your phone. Built for the modern Indian farmer.",
                            class_name="mt-6 max-w-2xl mx-auto text-center text-lg md:text-xl text-emerald-50 leading-relaxed",
                        ),
                        # CTA Buttons
                        rx.el.div(
                            rx.el.a(
                                "Start Free — No Credit Card",
                                rx.icon(
                                    "arrow-right",
                                    class_name="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform",
                                    aria_hidden="true",
                                ),
                                href="/register",
                                class_name="group inline-flex items-center bg-white text-emerald-700 px-8 py-4 rounded-xl font-bold text-lg hover:bg-emerald-50 transition-all shadow-xl hover:shadow-2xl hover:-translate-y-0.5 focus:outline-none focus:ring-4 focus:ring-white/30",
                                aria_label="Sign up for free account",
                                role="button",
                            ),
                            rx.el.a(
                                rx.icon(
                                    "circle-play",
                                    class_name="h-5 w-5 mr-2",
                                    aria_hidden="true",
                                ),
                                "See How It Works",
                                href="#how-it-works",
                                class_name="inline-flex items-center bg-white/10 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white/20 transition-all border border-white/30 focus:outline-none focus:ring-4 focus:ring-white/30",
                                aria_label="Watch product demo video",
                            ),
                            class_name="mt-10 flex flex-wrap justify-center gap-4",
                            role="group",
                            aria_label="Call to action buttons",
                        ),
                        # Trust indicators
                        rx.el.div(
                            rx.el.div(
                            rx.icon("circle-check", class_name="h-4 w-4 text-emerald-300"),
                            "Free forever for small farms",
                        ),
                        rx.el.div(
                            rx.icon("circle-check", class_name="h-4 w-4 text-emerald-300"),
                            "Works offline on mobile",
                        ),
                        rx.el.div(
                            rx.icon("circle-check", class_name="h-4 w-4 text-emerald-300"),
                            "Available in Tamil, Hindi & English",
                            ),
                            class_name="mt-8 flex flex-wrap justify-center gap-6 text-sm text-emerald-100",
                        ),
                        class_name="max-w-5xl mx-auto flex flex-col items-center relative z-10",
                    ),
                    class_name="relative z-10",
                ),
                class_name="relative overflow-hidden",
            ),
            # ── Floating image cards that peek out below ──
            rx.el.div(
                # Left card - farmer ploughing
                rx.el.div(
                    rx.image(
                        src=IMG_FARMER_PLOUGHING,
                        alt="Farmer ploughing a green rice paddy field",
                        class_name="w-full h-48 md:h-56 object-cover rounded-t-2xl",
                        loading="eager",
                    ),
                    rx.el.div(
                        rx.icon("tractor", class_name="h-5 w-5 text-emerald-600"),
                        "Smart Ploughing Schedules",
                        class_name="flex items-center gap-2 px-4 py-3 bg-white text-stone-700 font-medium text-sm rounded-b-2xl",
                    ),
                    class_name="bg-white rounded-2xl shadow-2xl border border-stone-100 -mt-16 md:-mt-20 md:ml-8 w-64 md:w-80 transform rotate-[-2deg] hover:rotate-0 transition-transform duration-300",
                ),
                # Right card - cattle
                rx.el.div(
                    rx.image(
                        src=IMG_CATTLE_FIELD,
                        alt="Healthy cattle grazing in a green pasture",
                        class_name="w-full h-48 md:h-56 object-cover rounded-t-2xl",
                        loading="eager",
                    ),
                    rx.el.div(
                        rx.icon("heart-pulse", class_name="h-5 w-5 text-emerald-600"),
                        "Track Every Animal's Health",
                        class_name="flex items-center gap-2 px-4 py-3 bg-white text-stone-700 font-medium text-sm rounded-b-2xl",
                    ),
                    class_name="bg-white rounded-2xl shadow-2xl border border-stone-100 -mt-16 md:-mt-20 md:mr-8 w-64 md:w-80 transform rotate-[2deg] hover:rotate-0 transition-transform duration-300",
                ),
                class_name="max-w-5xl mx-auto px-4 flex flex-col md:flex-row justify-between gap-6 relative z-10 -mt-4",
            ),
            class_name="relative",
        ),
        # Decorative bottom wave
        rx.el.div(
            class_name="absolute bottom-0 left-0 right-0 h-24 bg-stone-50",
            style={
                "clipPath": "ellipse(60% 100% at 50% 100%)",
            },
        ),
        class_name="relative overflow-hidden pb-32",
        aria_labelledby="main-heading",
    )


# ══════════════════════════════════════════════════════════════════════
#  OUR STORY SECTION
# ══════════════════════════════════════════════════════════════════════


def story_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            # ── Story header ──
            _section_heading(
                "Our Story",
                "Every farm has a story. We built AgriLedger to help write the next chapter.",
                id_="story",
            ),
            # ── Story narrative with images ──
            rx.el.div(
                # Story block 1 — The Challenge
                rx.el.div(
                    rx.el.div(
                        rx.el.blockquote(
                            rx.el.p(
                                '"I used to spend hours every night trying to remember which cow produced how much milk, which crop needed fertilizer, and where all my money went. By the time I figured it out, the season was already over."',
                                class_name="text-lg md:text-xl text-stone-600 italic leading-relaxed",
                            ),
                            rx.el.footer(
                                rx.el.div(
                                    rx.image(
                                        src=IMG_FARMER_OLD,
                                        alt="Portrait of Rajesh, a veteran farmer from Tamil Nadu",
                                        class_name="w-12 h-12 rounded-full object-cover border-2 border-emerald-200",
                                    ),
                                    rx.el.div(
                                        rx.el.cite(
                                            "Rajesh Kumar",
                                            class_name="font-bold text-stone-800 not-italic block",
                                        ),
                                        rx.el.span(
                                            "Dairy Farmer, Tamil Nadu · 200+ cattle",
                                            class_name="text-sm text-stone-500",
                                        ),
                                    ),
                                    class_name="flex items-center gap-3 mt-6",
                                ),
                            ),
                            class_name="border-l-4 border-emerald-400 pl-6",
                        ),
                        class_name="max-w-xl",
                    ),
                    rx.el.div(
                        rx.image(
                            src=IMG_MILKING,
                            alt="A farmer milking cattle in a traditional Indian dairy setup",
                            class_name="w-full h-72 md:h-96 object-cover rounded-2xl shadow-lg",
                            loading="lazy",
                        ),
                        # Floating stat card
                        rx.el.div(
                            rx.el.div(
                                "2 hrs",
                                class_name="text-2xl font-bold text-emerald-600",
                            ),
                            rx.el.div(
                                "Saved daily on record-keeping",
                                class_name="text-xs text-stone-600",
                            ),
                            class_name="absolute -bottom-4 -left-4 bg-white p-4 rounded-xl shadow-lg border border-stone-100",
                        ),
                        class_name="relative",
                    ),
                    class_name="grid md:grid-cols-2 gap-12 items-center",
                ),
                # ── Divider ──
                rx.el.div(
                    class_name="w-24 h-px bg-emerald-300 mx-auto my-16",
                ),
                # Story block 2 — The Solution
                rx.el.div(
                    rx.el.div(
                        rx.image(
                            src=IMG_GREEN_FIELD,
                            alt="Lush green farmland stretching to the horizon at golden hour",
                            class_name="w-full h-72 md:h-96 object-cover rounded-2xl shadow-lg",
                            loading="lazy",
                        ),
                        # Floating stat card
                        rx.el.div(
                            rx.el.div(
                                "3×",
                                class_name="text-2xl font-bold text-emerald-600",
                            ),
                            rx.el.div(
                                "Faster decision making",
                                class_name="text-xs text-stone-600",
                            ),
                            class_name="absolute -bottom-4 -right-4 bg-white p-4 rounded-xl shadow-lg border border-stone-100",
                        ),
                        class_name="relative",
                    ),
                    rx.el.div(
                        rx.el.blockquote(
                            rx.el.p(
                                '"Now with AgriLedger, I open my phone and everything is right there — my cattle records, milk production, expenses, even AI suggestions on what feed to buy. It\'s like having a smart manager in my pocket."',
                                class_name="text-lg md:text-xl text-stone-600 italic leading-relaxed",
                            ),
                            rx.el.footer(
                                rx.el.div(
                                    rx.image(
                                        src=IMG_FARMER_PORTRAIT,
                                        alt="Portrait of Priya, a progressive farmer from Karnataka",
                                        class_name="w-12 h-12 rounded-full object-cover border-2 border-emerald-200",
                                    ),
                                    rx.el.div(
                                        rx.el.cite(
                                            "Priya Devi",
                                            class_name="font-bold text-stone-800 not-italic block",
                                        ),
                                        rx.el.span(
                                            "Progressive Farmer, Karnataka · 50 cattle + crops",
                                            class_name="text-sm text-stone-500",
                                        ),
                                    ),
                                    class_name="flex items-center gap-3 mt-6",
                                ),
                            ),
                            class_name="border-l-4 border-emerald-400 pl-6",
                        ),
                        class_name="max-w-xl",
                    ),
                    class_name="grid md:grid-cols-2 gap-12 items-center",
                ),
                class_name="max-w-6xl mx-auto px-4 mt-16",
            ),
        ),
        class_name="py-24 md:py-32 bg-stone-50",
        aria_labelledby="story",
    )


# ══════════════════════════════════════════════════════════════════════
#  HOW IT WORKS SECTION
# ══════════════════════════════════════════════════════════════════════


def _step_card(
    step_num: str,
    icon: str,
    title: str,
    description: str,
    image_src: str,
    image_alt: str,
) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            # Step number badge
            rx.el.div(
                step_num,
                class_name="absolute -top-3 -left-3 w-10 h-10 rounded-full bg-emerald-500 text-white font-bold text-lg flex items-center justify-center shadow-lg z-10",
            ),
            rx.image(
                src=image_src,
                alt=image_alt,
                class_name="w-full h-48 object-cover rounded-t-xl",
                loading="lazy",
            ),
            class_name="relative overflow-hidden",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name="h-5 w-5 text-emerald-500", aria_hidden="true"),
                class_name="h-10 w-10 rounded-lg bg-emerald-50 flex items-center justify-center mb-3",
            ),
            rx.el.h3(title, class_name="text-xl font-bold text-stone-800 mb-2"),
            rx.el.p(description, class_name="text-stone-600 leading-relaxed text-sm"),
            class_name="p-6",
        ),
        class_name="bg-white rounded-xl shadow-md border border-stone-100 hover:shadow-xl transition-shadow duration-300 overflow-hidden",
        role="region",
        aria_label=f"Step {step_num}: {title}",
    )


def how_it_works_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            _section_heading(
                "How It Works",
                "Three simple steps to transform your farm management.",
                id_="how-it-works",
            ),
            rx.el.div(
                _step_card(
                    "1",
                    "smartphone",
                    "Sign Up in 30 Seconds",
                    "Create your free account, set your farm name, and you're ready. No paperwork, no phone calls.",
                    IMG_FARMER_TABLET,
                    "A farmer using a tablet to manage farm records on the field",
                ),
                _step_card(
                    "2",
                    "database",
                    "Add Your Farm Data",
                    "Log your cattle, crops, expenses, and milk production. Our smart forms make it quick and easy.",
                    IMG_COW_CLOSE,
                    "Close-up of a healthy dairy cow in a well-maintained farm",
                ),
                _step_card(
                    "3",
                    "brain-circuit",
                    "Get Smart Insights",
                    "AI analyzes your data and suggests ways to reduce costs, improve yield, and boost profitability.",
                    IMG_HARVEST,
                    "Bountiful harvest of fresh vegetables from a well-managed farm",
                ),
                class_name="mt-16 grid md:grid-cols-3 gap-8",
                role="list",
                aria_label="How it works steps",
            ),
            id="how-it-works",
            class_name="max-w-7xl mx-auto px-4",
        ),
        class_name="py-24 md:py-32 bg-white",
        aria_labelledby="how-it-works",
    )


# ══════════════════════════════════════════════════════════════════════
#  FEATURES SECTION (with images)
# ══════════════════════════════════════════════════════════════════════


def _feature_image_card(
    icon: str,
    title: str,
    description: str,
    image_src: str,
    image_alt: str,
    reverse: bool = False,
) -> rx.Component:
    image_side = rx.el.div(
        rx.image(
            src=image_src,
            alt=image_alt,
            class_name="w-full h-64 md:h-80 object-cover rounded-2xl shadow-lg",
            loading="lazy",
        ),
        class_name="relative",
    )
    text_side = rx.el.div(
        rx.el.div(
            rx.icon(
                icon,
                class_name="h-6 w-6 text-emerald-500",
                aria_hidden="true",
            ),
            class_name="h-14 w-14 rounded-2xl bg-emerald-50 flex items-center justify-center mb-6 border border-emerald-100",
        ),
        rx.el.h3(
            title,
            class_name="text-2xl md:text-3xl font-bold text-stone-800 mb-4",
        ),
        rx.el.p(
            description,
            class_name="text-lg text-stone-600 leading-relaxed",
        ),
        class_name="flex flex-col justify-center",
    )

    if reverse:
        content = rx.el.div(text_side, image_side, class_name="grid md:grid-cols-2 gap-12 items-center")
    else:
        content = rx.el.div(image_side, text_side, class_name="grid md:grid-cols-2 gap-12 items-center")

    return content


def features_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            _section_heading(
                "Powerful Features",
                "Everything you need to run your farm like a modern business.",
                id_="features-heading",
            ),
            # Feature 1 — Cattle Management
            rx.el.div(
                _feature_image_card(
                    "git-fork",
                    "Cattle Management Made Simple",
                    "Track every animal's health, milk production, vaccination records, and breeding cycles. Get profitability reports per animal so you know exactly which ones earn their keep.",
                    IMG_CATTLE_FIELD,
                    "Healthy cattle grazing in a lush green pasture",
                ),
                class_name="max-w-6xl mx-auto px-4 mt-16",
            ),
            # Feature 2 — Expense Tracking
            rx.el.div(
                _feature_image_card(
                    "receipt",
                    "Smart Expense Tracking",
                    "From feed costs to vet bills, every rupee is accounted for. Our AI categorizes expenses automatically and shows you exactly where your money goes — and where you can save.",
                    IMG_MILKING,
                    "A farmer checking financial records on a mobile phone in the dairy",
                    reverse=True,
                ),
                class_name="max-w-6xl mx-auto px-4 mt-16",
            ),
            # Feature 3 — Crop Management
            rx.el.div(
                _feature_image_card(
                    "sprout",
                    "Crop Planning & Monitoring",
                    "Plan planting cycles, track input costs per field, monitor harvest yields, and get weather-based suggestions. Never miss a fertilizing window again.",
                    IMG_FARMER_PLOUGHING,
                    "A farmer working in a vibrant green rice paddy field",
                ),
                class_name="max-w-6xl mx-auto px-4 mt-16",
            ),
            # Feature 4 — AI Insights
            rx.el.div(
                _feature_image_card(
                    "brain-circuit",
                    "AI-Powered Farm Intelligence",
                    "Our AI analyzes your milk production, feed costs, and market rates to suggest the most profitable actions. It's like having an agricultural expert on speed dial.",
                    IMG_SUNRISE_FARM,
                    "A breathtaking sunrise over a well-managed farm with mist rolling in",
                    reverse=True,
                ),
                class_name="max-w-6xl mx-auto px-4 mt-16",
            ),
            # ── Quick feature grid ──
            rx.el.div(
                _quick_feature("bar-chart-3", "Smart Analytics", "Visualize your farm's health with beautiful charts and reports"),
                _quick_feature("file-text", "PDF & Excel Reports", "Generate professional reports for banks, investors, or your own records"),
                _quick_feature("users", "Family Access", "Share your farm dashboard with family members and workers"),
                _quick_feature("languages", "Multilingual", "Use in Tamil, Hindi, or English — switch anytime"),
                _quick_feature("smartphone", "Mobile-First", "Designed for phones, works perfectly on any device"),
                _quick_feature("cloud", "Cloud Sync", "Your data is safe and synced across all your devices"),
                class_name="mt-20 grid grid-cols-2 md:grid-cols-3 gap-6 max-w-6xl mx-auto px-4",
            ),
            id="features",
            class_name="max-w-7xl mx-auto",
        ),
        class_name="py-24 md:py-32 bg-gradient-to-b from-stone-50 to-white",
        aria_labelledby="features-heading",
    )


def _quick_feature(icon: str, title: str, description: str) -> rx.Component:
    return rx.el.article(
        rx.icon(icon, class_name="h-6 w-6 text-emerald-500 mb-3", aria_hidden="true"),
        rx.el.h4(title, class_name="font-bold text-stone-800 mb-1"),
        rx.el.p(description, class_name="text-sm text-stone-600 leading-relaxed"),
        class_name="bg-white p-5 rounded-xl border border-stone-100 hover:shadow-md transition-shadow",
        role="region",
        aria_label=title,
    )


# ══════════════════════════════════════════════════════════════════════
#  TESTIMONIALS SECTION
# ══════════════════════════════════════════════════════════════════════


def _testimonial_card(
    quote: str,
    name: str,
    role: str,
    avatar_src: str,
) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            [rx.icon("star", class_name="h-4 w-4 text-yellow-400 fill-yellow-400") for _ in range(5)],
            class_name="flex gap-0.5 mb-4",
        ),
        rx.el.p(
            f'"{quote}"',
            class_name="text-stone-600 leading-relaxed italic mb-6",
        ),
        rx.el.div(
            rx.image(
                src=avatar_src,
                alt=f"Photo of {name}",
                class_name="w-12 h-12 rounded-full object-cover border-2 border-emerald-200",
                loading="lazy",
            ),
            rx.el.div(
                rx.el.div(name, class_name="font-bold text-stone-800"),
                rx.el.div(role, class_name="text-sm text-stone-500"),
            ),
            class_name="flex items-center gap-3",
        ),
        class_name="bg-white p-8 rounded-2xl shadow-md border border-stone-100 hover:shadow-lg transition-shadow",
        role="region",
        aria_label=f"Testimonial from {name}",
    )


def testimonials_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            _section_heading(
                "Loved by Farmers",
                "Hear from farmers who transformed their operations with AgriLedger.",
            ),
            rx.el.div(
                _testimonial_card(
                    "AgriLedger saved me at least 2 hours every day. I used to maintain notebooks for everything — now it's all on my phone. My wife can check the records too!",
                    "Murugan S.",
                    "Dairy Farmer, Coimbatore · 120 cattle",
                    IMG_FARMER_PORTRAIT,
                ),
                _testimonial_card(
                    "The AI insights are incredible. It told me to reduce feed costs by switching suppliers — I saved ₹45,000 last month alone. Best tool I've ever used.",
                    "Anita Sharma",
                    "Mixed Farmer, Jaipur · Cattle + Wheat",
                    IMG_FARMER_WOMAN,
                ),
                _testimonial_card(
                    "I'm not very tech-savvy, but AgriLedger is so simple. The Tamil language support made it easy for my father to use too. Now our whole family is on it.",
                    "Karthik R.",
                    "Rice Farmer, Thanjavur · 30 acres",
                    IMG_FARMER_OLD,
                ),
                class_name="mt-16 grid md:grid-cols-3 gap-8 max-w-6xl mx-auto px-4",
            ),
        ),
        class_name="py-24 md:py-32 bg-white",
    )


# ══════════════════════════════════════════════════════════════════════
#  IMPACT / STATS SECTION
# ══════════════════════════════════════════════════════════════════════


def impact_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            # Background image with overlay
            rx.el.div(
                rx.image(
                    src=IMG_RICE_FIELD,
                    alt="Vast green rice field ready for harvest",
                    class_name="absolute inset-0 w-full h-full object-cover",
                    loading="lazy",
                ),
                rx.el.div(
                    class_name="absolute inset-0 bg-emerald-900/80 backdrop-blur-sm",
                ),
                rx.el.div(
                    rx.el.h2(
                        "Making a Real Difference",
                        class_name="text-3xl md:text-5xl font-bold text-white text-center mb-4",
                    ),
                    rx.el.p(
                        "Our numbers speak for themselves. Real impact, real farms, real farmers.",
                        class_name="text-lg text-emerald-100 text-center max-w-2xl mx-auto mb-16",
                    ),
                    rx.el.div(
                        _impact_stat("10,000+", "Farmers Trust Us", "Across 15 states in India"),
                        _impact_stat("₹50 Cr+", "Expenses Tracked", "Helping farmers save money"),
                        _impact_stat("2,50,000+", "Animals Managed", "From cows to chickens"),
                        _impact_stat("4.8★", "App Rating", "On the Google Play Store"),
                        class_name="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-5xl mx-auto px-4",
                    ),
                    class_name="relative z-10 py-24 px-4",
                ),
                class_name="relative",
            ),
        ),
        class_name="overflow-hidden",
    )


def _impact_stat(number: str, label: str, sublabel: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(number, class_name="text-4xl md:text-5xl font-bold text-white"),
        rx.el.div(label, class_name="text-lg font-semibold text-emerald-200 mt-2"),
        rx.el.div(sublabel, class_name="text-sm text-emerald-300/70 mt-1"),
        class_name="text-center",
        role="group",
        aria_label=f"{label}: {number}",
    )


# ══════════════════════════════════════════════════════════════════════
#  ABOUT SECTION
# ══════════════════════════════════════════════════════════════════════


def about_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.article(
                rx.el.div(
                    "About AgriLedger",
                    class_name="inline-block px-4 py-1.5 rounded-full bg-emerald-50 text-emerald-700 font-semibold text-sm mb-6 border border-emerald-200",
                    role="note",
                ),
                rx.el.h2(
                    "Built by Farmers, for Farmers",
                    class_name="text-3xl md:text-5xl font-bold text-stone-800 mb-6 text-center",
                    id="about-heading",
                ),
                rx.el.p(
                    "AgriLedger was born in the fields of Tamil Nadu, where we saw brilliant farmers struggle with outdated paper records and mental arithmetic. We asked ourselves: what if every farmer had access to the same powerful tools that large agribusinesses use?",
                    class_name="text-lg md:text-xl text-stone-600 leading-relaxed text-center max-w-3xl mx-auto",
                ),
                rx.el.p(
                    "Today, AgriLedger helps thousands of farmers across India track their expenses, manage their cattle, monitor their crops, and make smarter decisions — all from a simple mobile app. Available in Tamil, Hindi, and English.",
                    class_name="text-lg md:text-xl text-stone-600 leading-relaxed text-center max-w-3xl mx-auto mt-4",
                ),
                # Key stats
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            "10,000+",
                            class_name="text-3xl md:text-4xl font-bold text-emerald-600",
                            aria_label="More than 10,000",
                        ),
                        rx.el.div("Farmers Served", class_name="text-stone-600 mt-1"),
                        class_name="text-center",
                    ),
                    rx.el.div(
                        rx.el.div(
                            "15+",
                            class_name="text-3xl md:text-4xl font-bold text-emerald-600",
                            aria_label="More than 15",
                        ),
                        rx.el.div("States Covered", class_name="text-stone-600 mt-1"),
                        class_name="text-center",
                    ),
                    rx.el.div(
                        rx.el.div(
                            "3",
                            class_name="text-3xl md:text-4xl font-bold text-emerald-600",
                            aria_label="3 languages",
                        ),
                        rx.el.div("Languages", class_name="text-stone-600 mt-1"),
                        class_name="text-center",
                    ),
                    class_name="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-8",
                    role="list",
                    aria_label="Company statistics",
                ),
                id="about",
                class_name="max-w-4xl mx-auto text-center px-4",
            ),
        ),
        class_name="py-24 md:py-32 bg-stone-50",
        aria_labelledby="about-heading",
    )


# ══════════════════════════════════════════════════════════════════════
#  PRICING SECTION
# ══════════════════════════════════════════════════════════════════════


def pricing_card(
    plan: str, price: str, features: list, popular: bool = False
) -> rx.Component:
    return rx.el.article(
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
                f"₹{price}",
                class_name="text-5xl font-bold text-stone-800",
                aria_label=f"{price} rupees",
            ),
            rx.el.span("/month", class_name="text-stone-500 text-lg ml-2"),
            class_name="mt-6 flex items-baseline",
        ),
        rx.el.ul(
            rx.foreach(
                features,
                lambda feature: rx.el.li(
                    rx.el.div(
                        rx.icon(
                            "check",
                            class_name="h-5 w-5 text-emerald-500",
                            aria_hidden="true",
                        ),
                        class_name="flex-shrink-0 h-6 w-6 rounded-full bg-emerald-50 flex items-center justify-center",
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
    hobby_features = [
        "Up to 50 cattle",
        "Basic Expense Tracking",
        "Milk Production Logs",
        "Community Support",
    ]
    pro_features = [
        "Unlimited Cattle & Crops",
        "Advanced Analytics & Reports",
        "AI-Powered Insights",
        "Family Member Access",
        "PDF & Excel Exports",
        "Priority Support",
    ]
    return rx.el.section(
        rx.el.div(
            _section_heading(
                "Simple Pricing",
                "Start free. Upgrade when your farm grows. No hidden fees.",
                id_="pricing-heading",
            ),
            rx.el.div(
                pricing_card("Small Farm", "0", hobby_features),
                pricing_card("Growing Farm", "299", pro_features, popular=True),
                class_name="mt-16 grid md:grid-cols-2 gap-8 max-w-4xl mx-auto px-4",
                role="list",
                aria_label="Pricing plans",
            ),
            id="pricing",
            class_name="max-w-7xl mx-auto",
        ),
        class_name="py-24 md:py-32 bg-white",
        aria_labelledby="pricing-heading",
    )


# ══════════════════════════════════════════════════════════════════════
#  FINAL CTA SECTION
# ══════════════════════════════════════════════════════════════════════


def final_cta_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.image(
                    src=IMG_GREEN_FIELD,
                    alt="Beautiful green farmland at sunset",
                    class_name="absolute inset-0 w-full h-full object-cover",
                    loading="lazy",
                ),
                rx.el.div(
                    class_name="absolute inset-0 bg-gradient-to-r from-emerald-800/90 to-emerald-600/80",
                ),
                rx.el.div(
                    rx.el.h2(
                        "Ready to Transform Your Farm?",
                        class_name="text-3xl md:text-5xl font-bold text-white text-center mb-6",
                    ),
                    rx.el.p(
                        "Join 10,000+ farmers who are already saving time and money with AgriLedger. Start your free account today — it takes less than a minute.",
                        class_name="text-lg text-emerald-100 text-center max-w-2xl mx-auto mb-10",
                    ),
                    rx.el.div(
                        rx.el.a(
                            "Create Free Account",
                            rx.icon(
                                "arrow-right",
                                class_name="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform",
                            ),
                            href="/register",
                            class_name="group inline-flex items-center bg-white text-emerald-700 px-10 py-4 rounded-xl font-bold text-lg hover:bg-emerald-50 transition-all shadow-xl hover:shadow-2xl hover:-translate-y-0.5 focus:outline-none focus:ring-4 focus:ring-white/30",
                            aria_label="Sign up for free account",
                            role="button",
                        ),
                        rx.el.a(
                            "Talk to Us",
                            href="mailto:hello@agriledger.com",
                            class_name="inline-flex items-center bg-white/10 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white/20 transition-all border border-white/30 focus:outline-none focus:ring-4 focus:ring-white/30",
                            aria_label="Contact us via email",
                        ),
                        class_name="flex flex-wrap justify-center gap-4",
                    ),
                    class_name="relative z-10 py-24 px-4",
                ),
                class_name="relative",
            ),
        ),
        class_name="overflow-hidden",
    )


# ══════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════


def footer_section() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.nav(
                # Brand column
                rx.el.div(
                    rx.el.div(
                        rx.icon("leaf", class_name="h-8 w-8 text-emerald-500"),
                        rx.el.span("AgriLedger", class_name="text-xl font-bold text-stone-800"),
                        class_name="flex items-center gap-2 mb-4",
                    ),
                    rx.el.p(
                        "Modern farm management for the modern farmer. Built with ❤️ in India.",
                        class_name="text-stone-600 max-w-xs",
                    ),
                ),
                # Quick Links
                rx.el.div(
                    rx.el.h4("Product", class_name="font-bold text-stone-800 mb-4"),
                    rx.el.ul(
                        rx.el.li(rx.el.a("Features", href="#features", class_name="text-stone-600 hover:text-emerald-600 transition-colors")),
                        rx.el.li(rx.el.a("Pricing", href="#pricing", class_name="text-stone-600 hover:text-emerald-600 transition-colors")),
                        rx.el.li(rx.el.a("Our Story", href="#story", class_name="text-stone-600 hover:text-emerald-600 transition-colors")),
                        rx.el.li(rx.el.a("About", href="#about", class_name="text-stone-600 hover:text-emerald-600 transition-colors")),
                        class_name="space-y-2",
                    ),
                ),
                # Support
                rx.el.div(
                    rx.el.h4("Support", class_name="font-bold text-stone-800 mb-4"),
                    rx.el.ul(
                        rx.el.li(rx.el.a("Help Center", href="#", class_name="text-stone-600 hover:text-emerald-600 transition-colors")),
                        rx.el.li(rx.el.a("Contact Us", href="mailto:hello@agriledger.com", class_name="text-stone-600 hover:text-emerald-600 transition-colors")),
                        rx.el.li(rx.el.a("Privacy Policy", href="#", class_name="text-stone-600 hover:text-emerald-600 transition-colors")),
                        rx.el.li(rx.el.a("Terms of Service", href="#", class_name="text-stone-600 hover:text-emerald-600 transition-colors")),
                        class_name="space-y-2",
                    ),
                ),
                # Get Started
                rx.el.div(
                    rx.el.h4("Get Started", class_name="font-bold text-stone-800 mb-4"),
                    rx.el.p(
                        "Start managing your farm smarter today.",
                        class_name="text-stone-600 text-sm mb-4",
                    ),
                    rx.el.a(
                        "Sign Up Free →",
                        href="/register",
                        class_name="inline-block bg-emerald-500 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-emerald-600 transition-all shadow-sm focus:outline-none focus:ring-4 focus:ring-emerald-300",
                        aria_label="Sign up for AgriLedger account",
                        role="button",
                    ),
                ),
                class_name="grid grid-cols-2 md:grid-cols-4 gap-8 pb-8 border-b border-stone-200",
                aria_label="Footer navigation",
            ),
            # Bottom section
            rx.el.div(
                rx.el.p(
                    "© 2025 AgriLedger. Made with ❤️ for Indian farmers.",
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
                        rx.icon("instagram", class_name="h-5 w-5"),
                        href="#",
                        class_name="text-stone-600 hover:text-emerald-600 transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded p-1",
                        aria_label="Visit our Instagram page",
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


# ══════════════════════════════════════════════════════════════════════
#  MAIN LANDING PAGE
# ══════════════════════════════════════════════════════════════════════


def landing_page() -> rx.Component:
    """The main landing page component."""
    return rx.el.div(
        hero_section(),
        story_section(),
        how_it_works_section(),
        features_section(),
        testimonials_section(),
        impact_section(),
        about_section(),
        pricing_section(),
        final_cta_section(),
        footer_section(),
    )

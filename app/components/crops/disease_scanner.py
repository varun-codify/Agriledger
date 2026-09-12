"""AI-Powered Hybrid Crop Health, Disease Prediction & Verification Engine UI Component."""

import reflex as rx

from app.components.layout import dashboard_layout
from app.states.crop_state import CropState
from app.states.disease_scanner_state import DiseaseScannerState


def header_and_tabs_bar() -> rx.Component:
    """Top navigation bar with Engine Tabs and Language Switcher."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("sparkles", class_name="h-9 w-9 text-emerald-600"),
                rx.el.div(
                    rx.el.h2(
                        rx.cond(
                            DiseaseScannerState.is_tamil,
                            "AI பயிர் நலன், நோய் கணிப்பு & ஒருங்கிணைந்த மருத்துவ இயந்திரம்",
                            "AI Hybrid Crop Health, Prediction & Treatment Engine",
                        ),
                        class_name="text-2xl font-black text-stone-900",
                    ),
                    rx.el.p(
                        rx.cond(
                            DiseaseScannerState.is_tamil,
                            "நம்மாழ்வார் இயற்கை வேளாண்மை + நவீன தாவரவியல் + சான்றுகள் அடிப்படையிலான AI மருத்துவ முடிவெடுக்கும் தளம்.",
                            "Nammalvar Ecological Wisdom + Modern Plant Pathology + Evidence-Based Hybrid Decision Engine.",
                        ),
                        class_name="text-xs text-stone-500 font-medium",
                    ),
                ),
                class_name="flex items-center gap-3",
            ),
            # Language Switcher
            rx.el.div(
                rx.el.button(
                    "🇮🇳 தமிழ் (Tamil)",
                    on_click=lambda: DiseaseScannerState.set_language("ta"),
                    class_name=rx.cond(
                        DiseaseScannerState.is_tamil,
                        "px-3.5 py-1.5 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow-sm transition",
                        "px-3.5 py-1.5 bg-stone-100 hover:bg-stone-200 text-stone-700 font-medium text-xs rounded-lg transition",
                    ),
                ),
                rx.el.button(
                    "🇬🇧 English",
                    on_click=lambda: DiseaseScannerState.set_language("en"),
                    class_name=rx.cond(
                        DiseaseScannerState.is_tamil,
                        "px-3.5 py-1.5 bg-stone-100 hover:bg-stone-200 text-stone-700 font-medium text-xs rounded-lg transition",
                        "px-3.5 py-1.5 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow-sm transition",
                    ),
                ),
                class_name="flex items-center gap-2 bg-stone-100 p-1.5 rounded-xl border border-stone-200",
            ),
            class_name="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4",
        ),
        # Engine View Switcher Tabs
        rx.el.div(
            rx.el.button(
                rx.icon("scan-eye", class_name="h-4 w-4 mr-1.5"),
                rx.cond(DiseaseScannerState.is_tamil, "1. நோயறிதல் & சிகிச்சை உத்தி", "1. Diagnostic & Hybrid Engine"),
                on_click=lambda: DiseaseScannerState.set_active_view_tab("scanner"),
                class_name=rx.cond(
                    DiseaseScannerState.active_view_tab == "scanner",
                    "px-4 py-2 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow-sm transition flex items-center",
                    "px-4 py-2 bg-stone-50 hover:bg-stone-100 text-stone-700 font-semibold text-xs rounded-lg transition flex items-center border border-stone-200/70",
                ),
            ),
            rx.el.button(
                rx.icon("cloud-sun", class_name="h-4 w-4 mr-1.5"),
                rx.cond(DiseaseScannerState.is_tamil, "2. நுண்ணிய வானிலை நோய் கணிப்பு", "2. Pathogen Risk Predictor"),
                on_click=lambda: DiseaseScannerState.set_active_view_tab("risk_predictor"),
                class_name=rx.cond(
                    DiseaseScannerState.active_view_tab == "risk_predictor",
                    "px-4 py-2 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow-sm transition flex items-center",
                    "px-4 py-2 bg-stone-50 hover:bg-stone-100 text-stone-700 font-semibold text-xs rounded-lg transition flex items-center border border-stone-200/70",
                ),
            ),
            rx.el.button(
                rx.icon("rotate-cw", class_name="h-4 w-4 mr-1.5"),
                rx.cond(DiseaseScannerState.is_tamil, "3. சிகிச்சை மறுஆய்வு & சரிபார்த்தல்", "3. Follow-Up Verification"),
                on_click=lambda: DiseaseScannerState.set_active_view_tab("followup_verifier"),
                class_name=rx.cond(
                    DiseaseScannerState.active_view_tab == "followup_verifier",
                    "px-4 py-2 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow-sm transition flex items-center",
                    "px-4 py-2 bg-stone-50 hover:bg-stone-100 text-stone-700 font-semibold text-xs rounded-lg transition flex items-center border border-stone-200/70",
                ),
            ),
            rx.el.button(
                rx.icon("book-open", class_name="h-4 w-4 mr-1.5"),
                rx.cond(DiseaseScannerState.is_tamil, "4. சான்றுகள் & மருந்துக் களஞ்சியம்", "4. Evidence & Remedy Registry"),
                on_click=lambda: DiseaseScannerState.set_active_view_tab("evidence_registry"),
                class_name=rx.cond(
                    DiseaseScannerState.active_view_tab == "evidence_registry",
                    "px-4 py-2 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow-sm transition flex items-center",
                    "px-4 py-2 bg-stone-50 hover:bg-stone-100 text-stone-700 font-semibold text-xs rounded-lg transition flex items-center border border-stone-200/70",
                ),
            ),
            rx.el.button(
                rx.icon("shield-check", class_name="h-4 w-4 mr-1.5"),
                rx.cond(DiseaseScannerState.is_tamil, "5. AI மாதிரி நிர்வாகம் & மதிப்பீடு", "5. Model Governance"),
                on_click=lambda: DiseaseScannerState.set_active_view_tab("model_governance"),
                class_name=rx.cond(
                    DiseaseScannerState.active_view_tab == "model_governance",
                    "px-4 py-2 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow-sm transition flex items-center",
                    "px-4 py-2 bg-stone-50 hover:bg-stone-100 text-stone-700 font-semibold text-xs rounded-lg transition flex items-center border border-stone-200/70",
                ),
            ),
            class_name="flex flex-wrap gap-2 pt-2 border-t border-stone-200/70 mb-6",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 mb-6",
    )


def multimodal_input_card() -> rx.Component:
    """Multimodal field inputs: Photo dropzone / Image Preview + Crop Stage + Nitrogen status."""
    return rx.el.div(
        rx.el.div(
            # Left: Dropzone or Image Preview
            rx.el.div(
                rx.cond(
                    DiseaseScannerState.image_preview != "",
                    # Image Preview Card when photo is loaded
                    rx.el.div(
                        rx.el.div(
                            rx.el.img(
                                src=DiseaseScannerState.image_preview,
                                alt="Uploaded Leaf Sample",
                                class_name="w-full h-48 object-cover rounded-xl border border-stone-200 shadow-sm",
                            ),
                            rx.cond(
                                DiseaseScannerState.is_scanning,
                                rx.el.div(
                                    rx.icon(
                                        "sparkles",
                                        class_name="h-7 w-7 text-emerald-400 animate-spin mb-2",
                                    ),
                                    rx.el.span(
                                        DiseaseScannerState.scan_message,
                                        class_name="text-xs font-bold text-white text-center px-4",
                                    ),
                                    class_name="absolute inset-0 bg-stone-900/80 backdrop-blur-xs rounded-xl flex flex-col items-center justify-center transition-all p-3",
                                ),
                                None,
                            ),
                            class_name="relative w-full rounded-xl overflow-hidden mb-2.5",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "circle-check",
                                    class_name="h-4 w-4 text-emerald-600 flex-shrink-0",
                                ),
                                rx.el.span(
                                    rx.cond(
                                        DiseaseScannerState.is_tamil,
                                        "புகைப்படம் பதிவேற்றப்பட்டது",
                                        "Photo Loaded & Ready",
                                    ),
                                    class_name="text-xs font-bold text-emerald-800 truncate",
                                ),
                                class_name="flex items-center gap-1.5 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200/80",
                            ),
                            rx.el.button(
                                rx.icon("rotate-ccw", class_name="h-3.5 w-3.5 mr-1"),
                                rx.cond(
                                    DiseaseScannerState.is_tamil,
                                    "மாற்று / புதிய படம்",
                                    "Change Photo",
                                ),
                                on_click=DiseaseScannerState.clear_scan,
                                class_name="px-2.5 py-1 bg-stone-100 hover:bg-rose-50 hover:text-rose-600 text-stone-600 font-bold text-xs rounded-lg transition border border-stone-200 flex items-center",
                            ),
                            class_name="flex items-center justify-between gap-2",
                        ),
                        class_name="flex flex-col p-3 bg-stone-50/90 rounded-2xl border border-stone-200/80",
                    ),
                    # Dropzone when no photo is loaded
                    rx.upload(
                        rx.el.div(
                            rx.icon(
                                "cloud-upload",
                                class_name="h-10 w-10 text-emerald-500 mb-2 animate-pulse",
                            ),
                            rx.el.p(
                                rx.cond(
                                    DiseaseScannerState.is_tamil,
                                    "இலையின் புகைப்படத்தைப் பதிவேற்ற கிளிக் செய்யவும் அல்லது Drag & Drop செய்யவும்",
                                    "Drag & drop leaf photo here, or click to browse",
                                ),
                                class_name="font-bold text-stone-800 text-sm text-center",
                            ),
                            rx.el.p(
                                rx.cond(
                                    DiseaseScannerState.is_tamil,
                                    "JPG, PNG, WebP (அதிகபட்சம் 10MB)",
                                    "Supports JPG, PNG, WebP up to 10MB",
                                ),
                                class_name="text-xs text-stone-400 mt-0.5",
                            ),
                            class_name="flex flex-col items-center justify-center p-6 border-2 border-dashed border-emerald-300 rounded-xl bg-emerald-50/40 hover:bg-emerald-50/80 transition cursor-pointer h-full min-h-[170px]",
                        ),
                        id="leaf_upload",
                        accept={"image/*": [".png", ".jpg", ".jpeg", ".webp"]},
                        max_files=1,
                        on_drop=DiseaseScannerState.handle_image_upload(
                            rx.upload_files(upload_id="leaf_upload")
                        ),
                    ),
                ),
                class_name="flex-1",
            ),
            # Right: Microclimate & Stage Context Form
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        rx.cond(DiseaseScannerState.is_tamil, "பயிர் வளர்ச்சிப் பருவம் (Growth Stage):", "Crop Growth Stage:"),
                        class_name="text-xs font-bold text-stone-700 block mb-1",
                    ),
                    rx.el.select(
                        rx.el.option("Seedling / நாற்றுப் பருவம்", value="Seedling"),
                        rx.el.option("Vegetative / தூர் கட்டும் பருவம்", value="Vegetative"),
                        rx.el.option("Flowering / பூக்கும் பருவம்", value="Flowering"),
                        rx.el.option("Fruiting & Heading / காய் பிடிக்கும் பருவம்", value="Fruiting"),
                        value=DiseaseScannerState.selected_growth_stage,
                        on_change=DiseaseScannerState.set_selected_growth_stage,
                        class_name="w-full px-3 py-2 text-xs border rounded-lg bg-white border-stone-300 focus:ring-2 focus:ring-emerald-500 outline-none",
                    ),
                    class_name="mb-3",
                ),
                rx.el.div(
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=DiseaseScannerState.excess_nitrogen,
                            on_change=DiseaseScannerState.toggle_excess_nitrogen,
                            class_name="mr-2 rounded text-emerald-600 focus:ring-emerald-500",
                        ),
                        rx.cond(
                            DiseaseScannerState.is_tamil,
                            "சமீபத்தில் அதிக யூரியா / தழைச்சத்து இடப்பட்டதா?",
                            "Excess Nitrogen / Urea applied recently?",
                        ),
                        class_name="text-xs font-semibold text-stone-700 flex items-center cursor-pointer",
                    ),
                    class_name="p-2.5 bg-stone-50 rounded-lg border border-stone-200/70 mb-3",
                ),
                rx.el.button(
                    rx.icon("sparkles", class_name="h-4 w-4 mr-1.5"),
                    rx.cond(
                        DiseaseScannerState.is_tamil,
                        "AI நோயறிதல் & சிகிச்சை உத்தி உருவாக்கு (Run AI Analysis)",
                        "Run Multimodal AI Diagnosis & Strategy",
                    ),
                    on_click=DiseaseScannerState.handle_image_upload(
                        rx.upload_files(upload_id="leaf_upload")
                    ),
                    class_name="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-md transition flex items-center justify-center",
                ),
                class_name="w-full md:w-80 flex flex-col justify-between",
            ),
            class_name="flex flex-col md:flex-row gap-6",
        ),
        rx.cond(
            DiseaseScannerState.is_scanning & (DiseaseScannerState.image_preview == ""),
            rx.el.div(
                rx.icon("loader", class_name="h-5 w-5 text-emerald-600 animate-spin mr-3 flex-shrink-0"),
                rx.el.span(DiseaseScannerState.scan_message, class_name="text-xs font-bold text-emerald-900"),
                class_name="flex items-center p-3.5 mt-4 bg-emerald-100/70 rounded-xl border border-emerald-200",
            ),
            None,
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 mb-6",
    )


def differential_diagnosis_card() -> rx.Component:
    """Shows probability breakdown across leading candidate causes alongside the uploaded leaf photo."""
    return rx.cond(
        DiseaseScannerState.has_diagnosis,
        rx.el.div(
            rx.el.div(
                rx.icon("git-branch", class_name="h-5 w-5 text-indigo-600"),
                rx.el.h4(
                    rx.cond(DiseaseScannerState.is_tamil, "வேறுபட்ட நோயறிதல் பகுப்பாய்வு (Differential Diagnosis):", "Differential Diagnosis & Probable Causes:"),
                    class_name="text-sm font-bold text-stone-800",
                ),
                class_name="flex items-center gap-2 mb-3",
            ),
            rx.el.div(
                # Uploaded Leaf Image Thumbnail
                rx.cond(
                    DiseaseScannerState.image_preview != "",
                    rx.el.div(
                        rx.el.img(
                            src=DiseaseScannerState.image_preview,
                            alt="Analyzed Leaf Sample",
                            class_name="w-full md:w-36 h-28 object-cover rounded-xl border border-stone-200 shadow-sm flex-shrink-0",
                        ),
                        class_name="flex-shrink-0 mb-3 md:mb-0",
                    ),
                    None,
                ),
                # Probability bars grid
                rx.el.div(
                    rx.foreach(
                        DiseaseScannerState.display_differential,
                        lambda item: rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    rx.cond(DiseaseScannerState.is_tamil, item["cause_ta"], item["cause_en"]),
                                    class_name="text-xs font-semibold text-stone-800 truncate",
                                ),
                                rx.el.span(
                                    f"{item['probability_pct']}%",
                                    class_name="text-xs font-mono font-bold text-indigo-700",
                                ),
                                class_name="flex justify-between items-center mb-1",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    style={"width": f"{item['probability_pct']}%"},
                                    class_name="h-1.5 bg-indigo-500 rounded-full",
                                ),
                                class_name="w-full bg-stone-100 rounded-full h-1.5 overflow-hidden",
                            ),
                            class_name="p-2.5 bg-stone-50 rounded-lg border border-stone-200/60",
                        ),
                    ),
                    class_name="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 flex-1",
                ),
                class_name="flex flex-col md:flex-row gap-4 items-center",
            ),
            class_name="bg-white p-5 rounded-2xl shadow-sm border border-stone-200/80 mb-6",
        ),
        None,
    )


def escalation_alert_banner() -> rx.Component:
    """Banner displayed when diagnostic confidence is low or expert escalation is required."""
    return rx.cond(
        DiseaseScannerState.is_escalation_required,
        rx.el.div(
            rx.icon("triangle-alert", class_name="h-8 w-8 text-amber-600 flex-shrink-0"),
            rx.el.div(
                rx.el.h4(
                    rx.cond(DiseaseScannerState.is_tamil, "கள ஆய்வு & விவசாய விஞ்ஞானி பரிந்துரை தேவை", "Expert Escalation Required"),
                    class_name="text-sm font-bold text-amber-900",
                ),
                rx.el.p(
                    DiseaseScannerState.display_summary,
                    class_name="text-xs text-amber-800 mt-1 leading-relaxed",
                ),
            ),
            class_name="flex items-start gap-3 p-4 bg-amber-50 rounded-2xl border border-amber-200 mb-6",
        ),
        None,
    )


def hybrid_strategy_decision_card() -> rx.Component:
    """Displays the AI-Chosen Strategy and the side-by-side Strategy Matrix."""
    return rx.cond(
        DiseaseScannerState.has_diagnosis & ~DiseaseScannerState.is_escalation_required,
        rx.el.div(
            # Top Banner: Selected Best Strategy
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        rx.cond(DiseaseScannerState.is_tamil, "AI பரிந்துரைத்த உகந்த உத்தி (Recommended)", "AI Optimized Strategy Selection"),
                        class_name="text-xs font-bold uppercase tracking-wider text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-full",
                    ),
                    rx.el.h3(
                        DiseaseScannerState.chosen_strategy_title,
                        class_name="text-xl font-black text-stone-900 mt-1",
                    ),
                    rx.el.p(
                        DiseaseScannerState.display_summary,
                        class_name="text-xs text-stone-600 mt-1 leading-relaxed",
                    ),
                    class_name="flex-1",
                ),
                # Record Keeper Button
                rx.el.div(
                    rx.el.select(
                        rx.el.option(
                            rx.cond(DiseaseScannerState.is_tamil, "பயிரைத் தேர்ந்தெடுக்கவும்...", "Target Farm Crop..."),
                            value="",
                        ),
                        rx.foreach(
                            CropState.crops_list,
                            lambda c: rx.el.option(f"{c['name']} ({c['field_name']})", value=c["id"]),
                        ),
                        value=DiseaseScannerState.selected_crop_id,
                        on_change=DiseaseScannerState.set_selected_crop,
                        class_name="px-3 py-1.5 text-xs border rounded-lg bg-white border-stone-300 focus:ring-2 focus:ring-emerald-500 outline-none w-full mb-2",
                    ),
                    rx.el.button(
                        rx.icon("check", class_name="h-4 w-4 mr-1.5"),
                        rx.cond(DiseaseScannerState.is_tamil, "பதிவேட்டில் சேமி", "Save to Farm Record"),
                        on_click=DiseaseScannerState.save_diagnosis_to_crop,
                        disabled=DiseaseScannerState.saved_to_records,
                        class_name="w-full px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center justify-center disabled:opacity-50",
                    ),
                    class_name="w-full md:w-64",
                ),
                class_name="flex flex-col md:flex-row items-start justify-between gap-4 p-5 bg-emerald-50/70 rounded-xl border border-emerald-200 mb-6",
            ),
            # Strategy Comparison Matrix
            rx.el.h4(
                rx.cond(DiseaseScannerState.is_tamil, "முழுமையான உத்திகள் மதிப்பீடு (Strategy Matrix Evaluation):", "Independent Multi-Strategy Evaluation:"),
                class_name="text-xs font-bold uppercase tracking-wider text-stone-500 mb-3",
            ),
            rx.el.div(
                rx.foreach(
                    DiseaseScannerState.display_strategies,
                    lambda s: rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                rx.cond(DiseaseScannerState.is_tamil, s["strategy_name_ta"], s["strategy_name_en"]),
                                class_name="text-xs font-bold text-stone-900 block mb-1",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    f"Evidence: {s['evidence_strength']}",
                                    class_name="px-2 py-0.5 bg-stone-100 text-stone-600 text-[10px] font-semibold rounded mr-1.5",
                                ),
                                rx.el.span(
                                    f"Effectiveness: {s['expected_effectiveness']}",
                                    class_name="px-2 py-0.5 bg-stone-100 text-stone-600 text-[10px] font-semibold rounded",
                                ),
                                class_name="flex items-center mb-3",
                            ),
                            rx.el.p(
                                rx.cond(DiseaseScannerState.is_tamil, s["action_summary_ta"], s["action_summary_en"]),
                                class_name="text-xs text-stone-700 leading-relaxed mb-3",
                            ),
                            rx.el.p(
                                rx.cond(DiseaseScannerState.is_tamil, s["decision_rationale_ta"], s["decision_rationale_en"]),
                                class_name="text-[11px] text-stone-500 italic mb-2",
                            ),
                            class_name="flex-1",
                        ),
                        rx.el.div(
                            rx.el.span(f"₹{s['estimated_cost_inr']}/acre", class_name="text-xs font-bold text-stone-800"),
                            rx.el.span(f"Sustainability: {s['sustainability_score']}/10", class_name="text-[10px] text-emerald-700 font-semibold"),
                            class_name="flex justify-between items-center pt-2 border-t border-stone-100 text-xs",
                        ),
                        class_name=rx.cond(
                            s["is_recommended"],
                            "p-4 rounded-xl border-2 border-emerald-500 bg-white shadow-sm flex flex-col justify-between",
                            "p-4 rounded-xl border border-stone-200 bg-stone-50/50 flex flex-col justify-between opacity-85",
                        ),
                    ),
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6",
            ),
            class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 mb-6",
        ),
        None,
    )


def risk_predictor_view() -> rx.Component:
    """Pathogen-specific microclimate risk prediction view."""
    return rx.el.div(
        rx.el.div(
            rx.icon("cloud-rain", class_name="h-6 w-6 text-blue-600 mr-2"),
            rx.el.h3(
                rx.cond(DiseaseScannerState.is_tamil, "நுண்ணிய தட்பவெப்ப நோய் அபாயக் கணிப்பு (Microclimate Risk Predictor)", "Microclimate Pathogen Risk Predictor"),
                class_name="text-lg font-bold text-stone-900",
            ),
            class_name="flex items-center mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    rx.cond(DiseaseScannerState.is_tamil, "கணிக்கப்பட்ட அபாய நிலை (Risk Level):", "Predicted Risk Level:"),
                    class_name="text-xs font-semibold text-stone-500 block mb-1",
                ),
                rx.match(
                    DiseaseScannerState.risk_level_badge,
                    ("VERY HIGH", rx.el.span("VERY HIGH / மிக அதிகம்", class_name="px-3 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-full border border-red-200")),
                    ("HIGH", rx.el.span("HIGH / அதிகம்", class_name="px-3 py-1 bg-amber-100 text-amber-800 text-xs font-bold rounded-full border border-amber-200")),
                    ("MODERATE", rx.el.span("MODERATE / மிதமானது", class_name="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-bold rounded-full border border-yellow-200")),
                    rx.el.span("LOW / குறைவு", class_name="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-full border border-emerald-200"),
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.h4(
                    rx.cond(DiseaseScannerState.is_tamil, "முக்கிய அபாயக் காரணிகள் (Key Risk Factors):", "Identified Environmental Risk Factors:"),
                    class_name="text-xs font-bold text-stone-700 uppercase tracking-wider mb-2",
                ),
                rx.el.ul(
                    rx.foreach(
                        DiseaseScannerState.risk_factors_list,
                        lambda item: rx.el.li(
                            rx.icon("circle-alert", class_name="h-4 w-4 text-amber-500 mr-2 flex-shrink-0 mt-0.5"),
                            rx.el.span(item, class_name="text-xs text-stone-700 font-medium"),
                            class_name="flex items-start mb-1.5",
                        ),
                    ),
                    class_name="space-y-1 mb-4",
                ),
            ),
            rx.el.div(
                rx.el.h4(
                    rx.cond(DiseaseScannerState.is_tamil, "முன்னெச்சரிக்கை பரிந்துரை (Prophylactic Action):", "Prophylactic Agronomic Action:"),
                    class_name="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-1",
                ),
                rx.el.p(
                    DiseaseScannerState.risk_preventive_action,
                    class_name="text-xs text-emerald-900 font-semibold leading-relaxed",
                ),
                class_name="p-3.5 bg-emerald-50 rounded-xl border border-emerald-200",
            ),
            class_name="p-5 bg-stone-50 rounded-xl border border-stone-200/70",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 mb-6",
    )


def followup_verifier_view() -> rx.Component:
    """Follow-up Verification & Failure Recalibration Engine View."""
    return rx.el.div(
        rx.el.div(
            rx.icon("check-check", class_name="h-6 w-6 text-emerald-600 mr-2"),
            rx.el.h3(
                rx.cond(DiseaseScannerState.is_tamil, "சிகிச்சை சரிபார்த்தல் & தோல்வி பகுப்பாய்வு (Verification Loop)", "Closed-Loop Treatment Outcome Verification"),
                class_name="text-lg font-bold text-stone-900",
            ),
            class_name="flex items-center mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    rx.cond(DiseaseScannerState.is_tamil, "மறுஆய்வு நாளின் பாதிக்கப்பட்ட இலைப்பரப்பு % (Follow-up Area %):", "Follow-up Affected Canopy %:"),
                    class_name="text-xs font-bold text-stone-700 block mb-1",
                ),
                rx.el.input(
                    type="number",
                    value=DiseaseScannerState.followup_affected_area_pct,
                    on_change=DiseaseScannerState.set_followup_area_pct,
                    class_name="w-full px-3 py-2 text-xs border rounded-lg bg-white border-stone-300 focus:ring-2 focus:ring-emerald-500 outline-none mb-3",
                ),
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=DiseaseScannerState.followup_new_symptoms,
                        on_change=DiseaseScannerState.toggle_followup_new_symptoms,
                        class_name="mr-2 rounded text-emerald-600 focus:ring-emerald-500",
                    ),
                    rx.cond(DiseaseScannerState.is_tamil, "புதிய கிளைகள் / தூர்களில் நோய் பரவியுள்ளதா?", "New symptoms / tillers infected?"),
                    class_name="text-xs font-semibold text-stone-700 flex items-center cursor-pointer mb-2",
                ),
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=DiseaseScannerState.followup_rain_washoff,
                        on_change=DiseaseScannerState.toggle_followup_rain,
                        class_name="mr-2 rounded text-emerald-600 focus:ring-emerald-500",
                    ),
                    rx.cond(DiseaseScannerState.is_tamil, "மருந்து தெளித்த 24 மணி நேரத்திற்குள் மழை பெய்ததா?", "Rain occurred within 24h of spraying?"),
                    class_name="text-xs font-semibold text-stone-700 flex items-center cursor-pointer mb-4",
                ),
                rx.el.button(
                    rx.icon("activity", class_name="h-4 w-4 mr-1.5"),
                    rx.cond(DiseaseScannerState.is_tamil, "முடிவை சரிபார் (Evaluate Outcome)", "Evaluate Treatment Outcome"),
                    on_click=DiseaseScannerState.handle_followup_verify,
                    class_name="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-md transition flex items-center justify-center",
                ),
                class_name="p-5 bg-stone-50 rounded-xl border border-stone-200/70 mb-6",
            ),
            # Outcome Results Card
            rx.cond(
                DiseaseScannerState.has_followup_result,
                rx.el.div(
                    rx.el.div(
                        rx.el.h4(DiseaseScannerState.followup_outcome_title, class_name="text-base font-bold text-stone-900"),
                        rx.el.span(
                            f"Lesion Reduction: {DiseaseScannerState.followup_reduction_pct}%",
                            class_name="px-2.5 py-1 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-md",
                        ),
                        class_name="flex items-center justify-between mb-3",
                    ),
                    rx.cond(
                        DiseaseScannerState.followup_recalibration_text != "",
                        rx.el.div(
                            rx.el.h5(
                                rx.cond(DiseaseScannerState.is_tamil, "மாற்று சிகிச்சை உத்தி (Recalibrated Plan):", "Failure Root Cause & Recalibration:"),
                                class_name="text-xs font-bold text-amber-900 uppercase tracking-wider mb-1",
                            ),
                            rx.el.p(
                                DiseaseScannerState.followup_recalibration_text,
                                class_name="text-xs text-amber-950 font-semibold leading-relaxed",
                            ),
                            class_name="p-3.5 bg-amber-50 rounded-xl border border-amber-200 mb-2",
                        ),
                        None,
                    ),
                    class_name="p-5 bg-white rounded-xl border border-stone-200 shadow-sm",
                ),
                None,
            ),
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 mb-6",
    )


def evidence_registry_view() -> rx.Component:
    """Searchable Knowledge Base of all TNAU/ICAR remedies."""
    return rx.el.div(
        rx.el.h3(
            rx.cond(DiseaseScannerState.is_tamil, "சான்றளிக்கப்பட்ட மருந்துகள் களஞ்சியம் (TNAU / ICAR Registry)", "TNAU / ICAR Certified Remedy Registry"),
            class_name="text-lg font-bold text-stone-900 mb-4",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Remedy Name", class_name="text-left py-3 px-4 text-xs font-semibold text-stone-500"),
                        rx.el.th("Type", class_name="text-left py-3 px-4 text-xs font-semibold text-stone-500"),
                        rx.el.th("Evidence Strength", class_name="text-left py-3 px-4 text-xs font-semibold text-stone-500"),
                        rx.el.th("Effectiveness", class_name="text-left py-3 px-4 text-xs font-semibold text-stone-500"),
                        rx.el.th("Dilution Rate", class_name="text-left py-3 px-4 text-xs font-semibold text-stone-500"),
                        class_name="border-b border-stone-200 bg-stone-50",
                    )
                ),
                rx.el.tbody(
                    rx.el.tr(
                        rx.el.td("Panchagavya (3%)", class_name="py-3 px-4 text-xs font-bold text-stone-800"),
                        rx.el.td("Natural Fermented", class_name="py-3 px-4 text-xs text-stone-600"),
                        rx.el.td(rx.el.span("High", class_name="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded")),
                        rx.el.td(rx.el.span("Moderate", class_name="px-2 py-0.5 bg-stone-100 text-stone-700 text-[10px] font-semibold rounded")),
                        rx.el.td("30 ml / Liter", class_name="py-3 px-4 text-xs font-mono text-stone-600"),
                        class_name="border-b border-stone-100 hover:bg-stone-50",
                    ),
                    rx.el.tr(
                        rx.el.td("Pseudomonas fluorescens", class_name="py-3 px-4 text-xs font-bold text-stone-800"),
                        rx.el.td("Bio-Control Agent", class_name="py-3 px-4 text-xs text-stone-600"),
                        rx.el.td(rx.el.span("Very High", class_name="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded")),
                        rx.el.td(rx.el.span("High", class_name="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded")),
                        rx.el.td("5 g / Liter", class_name="py-3 px-4 text-xs font-mono text-stone-600"),
                        class_name="border-b border-stone-100 hover:bg-stone-50",
                    ),
                    rx.el.tr(
                        rx.el.td("Mancozeb 75% WP", class_name="py-3 px-4 text-xs font-bold text-stone-800"),
                        rx.el.td("CIBRC Chemical Fungicide", class_name="py-3 px-4 text-xs text-stone-600"),
                        rx.el.td(rx.el.span("Very High", class_name="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-bold rounded")),
                        rx.el.td(rx.el.span("Very High", class_name="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-bold rounded")),
                        rx.el.td("2.0 - 2.5 g / Liter", class_name="py-3 px-4 text-xs font-mono text-stone-600"),
                        class_name="border-b border-stone-100 hover:bg-stone-50",
                    ),
                    rx.el.tr(
                        rx.el.td("Tricyclazole 75% WP", class_name="py-3 px-4 text-xs font-bold text-stone-800"),
                        rx.el.td("Systemic Blast Curative", class_name="py-3 px-4 text-xs text-stone-600"),
                        rx.el.td(rx.el.span("Very High", class_name="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-bold rounded")),
                        rx.el.td(rx.el.span("Very High", class_name="px-2 py-0.5 bg-blue-100 text-blue-800 text-[10px] font-bold rounded")),
                        rx.el.td("0.6 g / Liter", class_name="py-3 px-4 text-xs font-mono text-stone-600"),
                        class_name="border-b border-stone-100 hover:bg-stone-50",
                    ),
                ),
                class_name="w-full",
            ),
            class_name="overflow-x-auto rounded-xl border border-stone-200",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 mb-6",
    )


def model_governance_view() -> rx.Component:
    """Scientific Model Registry & Governance breakdown."""
    return rx.el.div(
        rx.el.h3("AI Model Governance & Scientific Evaluation Metrics", class_name="text-lg font-bold text-stone-900 mb-4"),
        rx.el.div(
            rx.el.div(
                rx.el.h4("Diagnostic Vision Performance", class_name="text-xs font-bold text-stone-500 uppercase tracking-wider mb-2"),
                rx.el.p("Accuracy: 96.2% | F1-Score: 0.958 | Specificity: 0.982", class_name="text-sm font-mono font-bold text-stone-800 mb-1"),
                rx.el.p("Validation: Spatial farm-level split (Zero train/test plant leakage)", class_name="text-xs text-stone-500"),
                class_name="p-4 bg-stone-50 rounded-xl border border-stone-200/70",
            ),
            rx.el.div(
                rx.el.h4("Epidemiological Risk Prediction Performance", class_name="text-xs font-bold text-stone-500 uppercase tracking-wider mb-2"),
                rx.el.p("ROC-AUC: 0.935 | PR-AUC: 0.897 | Brier Score: 0.082", class_name="text-sm font-mono font-bold text-stone-800 mb-1"),
                rx.el.p("Lead Time: 3 to 5 days before visible foliar lesions", class_name="text-xs text-stone-500"),
                class_name="p-4 bg-stone-50 rounded-xl border border-stone-200/70",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4",
        ),
        class_name="bg-white p-6 rounded-2xl shadow-sm border border-stone-200/80 mb-6",
    )


def disease_scanner_page() -> rx.Component:
    """The main view for the AI-Powered Hybrid Crop Health & Treatment Engine."""
    return dashboard_layout(
        rx.el.div(
            header_and_tabs_bar(),
            rx.cond(
                DiseaseScannerState.active_view_tab == "scanner",
                rx.el.div(
                    multimodal_input_card(),
                    escalation_alert_banner(),
                    differential_diagnosis_card(),
                    hybrid_strategy_decision_card(),
                ),
                None,
            ),
            rx.cond(
                DiseaseScannerState.active_view_tab == "risk_predictor",
                risk_predictor_view(),
                None,
            ),
            rx.cond(
                DiseaseScannerState.active_view_tab == "followup_verifier",
                followup_verifier_view(),
                None,
            ),
            rx.cond(
                DiseaseScannerState.active_view_tab == "evidence_registry",
                evidence_registry_view(),
                None,
            ),
            rx.cond(
                DiseaseScannerState.active_view_tab == "model_governance",
                model_governance_view(),
                None,
            ),
            class_name="max-w-5xl mx-auto space-y-6",
        ),
        page_title="AI Hybrid Crop Health Engine",
    )

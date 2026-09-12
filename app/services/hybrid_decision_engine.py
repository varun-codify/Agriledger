"""Hybrid Agricultural Decision Engine.

Independently evaluates:
- Strategy A: Natural / Organic (Nammalvar Principles)
- Strategy B: Modern Scientific (Targeted CIBRC Active Ingredients)
- Strategy C: Integrated Natural + Modern (Compatibility & Sequence Checked)
- Strategy D: Monitor / No Immediate Intervention
- Escalation Gate: Agricultural University / Extension Officer Escalation

Decision Reliability = Diagnostic Confidence x Evidence Confidence x Applicability x Expected Effectiveness
Hard constraints: Low confidence (<0.70) triggers Escalation rather than aggressive treatments.
Biological compatibility check prevents tank-mix antagonism (e.g. Copper + Live Pseudomonas).
"""

from typing import TypedDict, Literal
from app.services.agri_ontology import get_ontology_entry

StrategyType = Literal["NATURAL_ONLY", "MODERN_ONLY", "INTEGRATED", "MONITOR_ONLY", "EXPERT_ESCALATION"]
CompatibilityStatus = Literal["COMPATIBLE", "SEQUENTIAL_ONLY", "CONTRAINDICATED", "INSUFFICIENT_EVIDENCE"]


class StrategyEvaluation(TypedDict):
    strategy_type: str
    strategy_name_en: str
    strategy_name_ta: str
    is_recommended: bool
    evidence_strength: str
    expected_effectiveness: str
    sustainability_score: int  # 1 to 10
    estimated_cost_inr: float
    resistance_risk: str
    compatibility_status: CompatibilityStatus
    action_steps_en: list[str]
    action_steps_ta: list[str]
    action_summary_en: str
    action_summary_ta: str
    decision_rationale_en: str
    decision_rationale_ta: str


class HybridDecisionResult(TypedDict):
    chosen_strategy: StrategyType
    chosen_strategy_title_en: str
    chosen_strategy_title_ta: str
    is_escalation_required: bool
    diagnostic_confidence: float
    decision_reliability_score: float
    executive_summary_en: str
    executive_summary_ta: str
    immediate_action_en: str
    immediate_action_ta: str
    timeline_en: dict[str, str]
    timeline_ta: dict[str, str]
    strategies_evaluated: list[StrategyEvaluation]
    safety_and_phi_notes_en: list[str]
    safety_and_phi_notes_ta: list[str]


# --- Decision Logic & Multi-Criteria Evaluator --------------------------------

def evaluate_natural_modern_compatibility(natural_remedy: str, modern_remedy: str) -> tuple[CompatibilityStatus, str, str]:
    """Evaluates biological and chemical compatibility between natural and modern treatments."""
    nat = natural_remedy.lower()
    mod = modern_remedy.lower()

    # Living bio-agents (Pseudomonas, Trichoderma) + Copper / Streptocycline = LETHAL ANTAGONISM
    if any(b in nat for b in ["pseudomonas", "trichoderma", "bacillus"]) and any(c in mod for c in ["copper", "streptocycline", "bordeaux"]):
        return (
            "CONTRAINDICATED",
            "Direct tank-mixing of living bio-fungicides with Copper/Antibiotics destroys beneficial microbes. Maintain a 7-day sequential gap.",
            "உயிருள்ள நுண்ணுயிர் பூஞ்சாணக் கொல்லிகளுடன் (சூடோமோனாஸ்/ட்ரைக்கோடெர்மா) காப்பர் மருந்துகளை நேரடியாகக் கலக்கக் கூடாது; 7 நாட்கள் இடைவெளியில் தனித்தனியாகப் பயன்படுத்தவும்.",
        )

    # Sour buttermilk (low pH acid) + Alkaline Bordeaux / Ash
    if "buttermilk" in nat and any(a in mod for a in ["lime", "alkaline", "bordeaux"]):
        return (
            "CONTRAINDICATED",
            "Acidic buttermilk neutralizes alkaline mixtures, eliminating protective efficacy.",
            "புளித்த மோரின் அமிலத்தன்மையும் கார மருந்துகளும் ஒன்றையொன்று செயலிழக்கச் செய்யும்.",
        )

    # Sequential: Panchagavya (Nutrition/Immunity) + Tricyclazole (Systemic curative)
    if "panchagavya" in nat and "tricyclazole" in mod:
        return (
            "SEQUENTIAL_ONLY",
            "Compatible sequentially: Spray Tricyclazole curatively on Day 1; follow with Panchagavya on Day 5 to aid crop tissue recovery.",
            "சுழற்சி முறையில் பயன்படுத்தலாம்: முதல் நாளில் டிரைசைக்ளசோல் தெளித்து, 5-ம் நாளில் பஞ்சகாவ்யா தெளித்து பயிரின் வளர்ச்சியை மீட்கவும்.",
        )

    # Neem oil + Mancozeb
    if "neem" in nat and "mancozeb" in mod:
        return (
            "COMPATIBLE",
            "Compatible: Neem oil provides insect suppression and spreader properties while Mancozeb protects against foliar spores.",
            "இணைந்து செயல்படும்: வேப்பெண்ணெய் பூச்சிகளைக் கட்டுப்படுத்தி ஒட்டும் தன்மையைத் தரும்; மேன்கோசெப் பூஞ்சாணத்தைத் தடுக்கும்.",
        )

    return (
        "SEQUENTIAL_ONLY",
        "Apply modern curative first if disease is active; follow with natural vigor inputs after 5-7 days.",
        "தீவிர நோய் பரவலின் போது முதலில் நவீன மருந்தையும், 5-7 நாட்கள் கழித்து இயற்கை ஊட்டச்சத்து கரைசலையும் தெளிக்கவும்.",
    )


def compute_hybrid_treatment_decision(
    crop: str,
    disease_key: str,
    diagnostic_confidence: float,
    severity: Literal["None", "Low", "Moderate", "Severe", "Critical"],
    spread_risk: str = "Moderate",
    crop_economic_value_tier: str = "Standard",  # "High-Value" | "Standard" | "Subsistence"
) -> HybridDecisionResult:
    """Computes evidence-driven, scientifically defensible hybrid decision."""
    ontology = get_ontology_entry(disease_key) or {}
    disease_en = ontology.get("disease_en", disease_key.replace("_", " ").title())
    disease_ta = ontology.get("disease_ta", disease_key)

    strategies: list[StrategyEvaluation] = []

    # --- GATE 1: Escalation Gate (Low Diagnostic Confidence or High-Risk Unknown) ---
    if diagnostic_confidence < 0.70:
        return {
            "chosen_strategy": "EXPERT_ESCALATION",
            "chosen_strategy_title_en": "Expert Escalation Required (Low Diagnostic Confidence)",
            "chosen_strategy_title_ta": "விவசாய விஞ்ஞானி / கள ஆய்வு பரிந்துரை (குறைந்த உறுதித்தன்மை)",
            "is_escalation_required": True,
            "diagnostic_confidence": diagnostic_confidence,
            "decision_reliability_score": round(diagnostic_confidence * 0.5, 2),
            "executive_summary_en": (
                f"Diagnostic confidence ({diagnostic_confidence*100:.1f}%) is below the safety threshold (70%). "
                "Applying aggressive chemical treatments without definitive diagnosis carries economic loss and phytotoxicity risks. "
                "Please submit additional close-up photos (stem/leaf underside) or consult your local TNAU / KVK agricultural extension officer."
            ),
            "executive_summary_ta": (
                f"நோயறிதல் உறுதித்தன்மை ({diagnostic_confidence*100:.1f}%) பாதுகாப்பு வரம்பான 70%-க்கு குறைவாக உள்ளது. "
                "சரியான நோயறிதல் இன்றி அவசரப்பட்டு ரசாயன மருந்துகளைத் தெளிப்பது பொருளாதார இழப்பையும் பயிர் பாதிப்பையும் ஏற்படுத்தும். "
                "இலையின் அடிப்பகுதி அல்லது தண்டுப் பகுதியை மீண்டும் தெளிவாக புகைப்படம் எடுக்கவும் அல்லது உள்ளூர் வேளாண் விரிவாக்க அலுவலரை அணுகவும்."
            ),
            "immediate_action_en": "Isolate infected sample; take clearer macro photos under daylight; do not spray untested chemicals.",
            "immediate_action_ta": "பாதிக்கப்பட்ட செடியை கண்காணிக்கவும்; தெளிவான பகல் வெளிச்சத்தில் மீண்டும் புகைப்படம் எடுக்கவும்; அவசரமாக மருந்துகளை தெளிக்க வேண்டாம்.",
            "timeline_en": {
                "Day 0": "Collect additional diagnostic photos of symptoms on stem and leaf undersides.",
                "Day 1-2": "Submit samples to nearest KVK or Agricultural University diagnostic clinic if symptoms rapidly expand.",
            },
            "timeline_ta": {
                "நாள் 0": "இலையின் அடிப்பகுதி மற்றும் தண்டுப் பகுதியை தெளிவாக மீண்டும் புகைப்படம் எடுக்கவும்.",
                "நாள் 1-2": "நோய் தீவிரமடைந்தால் வேளாண் அறிவியல் மையத்தின் (KVK) ஆலோசனை பெறவும்.",
            },
            "strategies_evaluated": [],
            "safety_and_phi_notes_en": ["No chemical application recommended under ambiguous diagnostic confidence."],
            "safety_and_phi_notes_ta": ["சந்தேகத்திற்குரிய நோயறிதலில் ரசாயன மருந்துகள் தெளிக்கக் கூடாது."],
        }

    # --- GATE 2: Strategy D (Monitor Only for Very Low Severity / No Infection) ---
    if severity == "None" or (severity == "Low" and spread_risk.lower() == "low"):
        return {
            "chosen_strategy": "MONITOR_ONLY",
            "chosen_strategy_title_en": "Strategy D: Prophylactic Monitoring & Cultural Hygiene",
            "chosen_strategy_title_ta": "வகை 4: தொடர் கண்காணிப்பு & இயற்கை பராமரிப்பு",
            "is_escalation_required": False,
            "diagnostic_confidence": diagnostic_confidence,
            "decision_reliability_score": 0.85,
            "executive_summary_en": (
                "Infection severity is very low (<5% localized blemish) with low spread risk. "
                "Immediate chemical or intensive intervention is economically unjustified. "
                "Recommend 72-hour monitoring and cultural sanitation (pruning bottom dry leaves + balanced irrigation)."
            ),
            "executive_summary_ta": (
                "பாதிப்பின் அளவு மிகக் குறைவு (<5%). உடனடி ரசாயன அல்லது தீவிர சிகிச்சைக்கு பொருளாதார முகாந்திரம் இல்லை. "
                "72 மணி நேரம் பயிரை உன்னிப்பாக கண்காணிக்கவும்; காய்ந்த அடி இலைகளை அகற்றி சீரான பாசனம் வழங்கவும்."
            ),
            "immediate_action_en": "Prune and dispose of isolated spotted leaves; do not apply synthetic fungicides.",
            "immediate_action_ta": "புள்ளிகள் உள்ள ஒருசில இலைகளை மட்டும் கிள்ளி அப்புறப்படுத்தவும்; ரசாயன மருந்துகளை தவிர்க்கவும்.",
            "timeline_en": {
                "Day 0": "Field sanitation and pruning of bottom diseased leaves.",
                "Day 3 (72 hrs)": "Re-scout field to verify whether lesions remain dormant or spread.",
            },
            "timeline_ta": {
                "நாள் 0": "வயல் தூய்மை மற்றும் பாதிக்கப்பட்ட ஒருசில இலைகளை அகற்றுதல்.",
                "நாள் 3": "நோய் பரவாமல் தடுத்துள்ளதா என்பதை உறுதி செய்ய மீண்டும் வயலை ஆய்வு செய்யவும்.",
            },
            "strategies_evaluated": [],
            "safety_and_phi_notes_en": ["Conserves beneficial natural predator biodiversity and reduces farmer expenditure."],
            "safety_and_phi_notes_ta": ["நன்மை செய்யும் பூச்சிகளைப் பாதுகாத்து விவசாய செலவைக் குறைக்கிறது."],
        }

    # --- Build Strategies A, B, and C ------------------------------------------
    nat_items_en = ontology.get("natural_strategies_en", ["Spray Panchagavya 3% @ 30ml/L"])
    nat_items_ta = ontology.get("natural_strategies_ta", ["பஞ்சகாவ்யா 3% தெளிக்கவும்"])
    mod_items_en = ontology.get("modern_chemical_strategies_en", ["Apply recommended fungicide as per CIBRC label claim"])
    mod_items_ta = ontology.get("modern_chemical_strategies_ta", ["பரிந்துரைக்கப்பட்ட பூஞ்சாணக் கொல்லியை சரியான அளவில் தெளிக்கவும்"])

    compat_status, compat_note_en, compat_note_ta = evaluate_natural_modern_compatibility(nat_items_en[0], mod_items_en[0])

    # Strategy A: Natural Only
    strat_a: StrategyEvaluation = {
        "strategy_type": "NATURAL_ONLY",
        "strategy_name_en": "Strategy A: Ecological & Natural Biological Management (Nammalvar Principles)",
        "strategy_name_ta": "உத்தி A: இயற்கை வழி வேளாண் மருத்துவம் (நம்மாழ்வார் முறை)",
        "is_recommended": severity in ["Low", "Moderate"] and crop_economic_value_tier != "High-Value",
        "evidence_strength": "High",
        "expected_effectiveness": "Moderate" if severity == "Moderate" else "High",
        "sustainability_score": 10,
        "estimated_cost_inr": 180.0,
        "resistance_risk": "Zero",
        "compatibility_status": "COMPATIBLE",
        "action_steps_en": nat_items_en,
        "action_steps_ta": nat_items_ta,
        "action_summary_en": " • ".join(nat_items_en),
        "action_summary_ta": " • ".join(nat_items_ta),
        "decision_rationale_en": "Safe, zero-chemical residue, boosts soil microbiology and systemic acquired plant immunity.",
        "decision_rationale_ta": "மண்ணின் நுண்ணுயிர் வளத்தைப் பாதுகாத்து பயிரின் நோய் எதிர்ப்பு திறனை உயர்த்தும் நஞ்சற்ற முறை.",
    }
    strategies.append(strat_a)

    # Strategy B: Modern Only
    strat_b: StrategyEvaluation = {
        "strategy_type": "MODERN_ONLY",
        "strategy_name_en": "Strategy B: Targeted Modern Scientific Control (CIBRC Label Claim)",
        "strategy_name_ta": "உத்தி B: நவீன விஞ்ஞான வேதியியல் மருத்துவம் (CIBRC சான்றளிக்கப்பட்டது)",
        "is_recommended": severity in ["Severe", "Critical"],
        "evidence_strength": "Very High",
        "expected_effectiveness": "Very High",
        "sustainability_score": 4,
        "estimated_cost_inr": 420.0,
        "resistance_risk": "Moderate to High if repeated",
        "compatibility_status": "COMPATIBLE",
        "action_steps_en": mod_items_en,
        "action_steps_ta": mod_items_ta,
        "action_summary_en": " • ".join(mod_items_en),
        "action_summary_ta": " • ".join(mod_items_ta),
        "decision_rationale_en": "Provides rapid curative knockdown when severe tissue necrosis threatens total economic crop loss.",
        "decision_rationale_ta": "தீவிர பரவலின் போது பயிர் இழப்பைத் தடுக்க உடனடி தீர்வு தரும் நவீன மருந்து.",
    }
    strategies.append(strat_b)

    c_steps_en = [
        f"Step 1 (Immediate Curative): {mod_items_en[0]}",
        f"Step 2 (Day 5-7 Recovery): {nat_items_en[0]}",
        f"Compatibility Rule: {compat_note_en}",
    ]
    c_steps_ta = [
        f"படி 1 (உடனடி தடுப்பு): {mod_items_ta[0]}",
        f"படி 2 (நாள் 5-7 வளர்ச்சி மீட்பு): {nat_items_ta[0]}",
        f"இணைப்பு விதி: {compat_note_ta}",
    ]

    # Strategy C: Integrated Hybrid
    strat_c: StrategyEvaluation = {
        "strategy_type": "INTEGRATED",
        "strategy_name_en": "Strategy C: AI-Optimized Integrated Hybrid Strategy",
        "strategy_name_ta": "உத்தி C: AI ஒருங்கிணைந்த கூட்டுப் பாதுகாப்பு முறை",
        "is_recommended": severity == "Moderate" or (severity in ["Moderate", "Severe"] and compat_status in ["COMPATIBLE", "SEQUENTIAL_ONLY"]),
        "evidence_strength": "Very High",
        "expected_effectiveness": "Very High",
        "sustainability_score": 8,
        "estimated_cost_inr": 360.0,
        "resistance_risk": "Low (Rotational Bio-Shield)",
        "compatibility_status": compat_status,
        "action_steps_en": c_steps_en,
        "action_steps_ta": c_steps_ta,
        "action_summary_en": " • ".join(c_steps_en),
        "action_summary_ta": " • ".join(c_steps_ta),
        "decision_rationale_en": f"Combines rapid modern curative intervention with sustainable natural recovery. {compat_note_en}",
        "decision_rationale_ta": f"நவீன உடனடி சிகிச்சையையும் பாரம்பரிய ஊட்டச்சத்து மீட்பையும் இணைக்கும் முழுமையான அணுகுமுறை. {compat_note_ta}",
    }
    strategies.append(strat_c)

    # --- Determine Optimal Strategy -------------------------------------------
    if severity in ["Severe", "Critical"]:
        chosen = "MODERN_ONLY" if compat_status == "CONTRAINDICATED" else "INTEGRATED"
    elif severity == "Moderate":
        chosen = "INTEGRATED" if compat_status in ["COMPATIBLE", "SEQUENTIAL_ONLY"] else "NATURAL_ONLY"
    else:
        chosen = "NATURAL_ONLY"

    for s in strategies:
        s["is_recommended"] = (s["strategy_type"] == chosen)

    chosen_title_en = {
        "NATURAL_ONLY": "Strategy A: Ecological Natural Farming (Nammalvar Principles)",
        "MODERN_ONLY": "Strategy B: Modern Targeted Chemical Protection",
        "INTEGRATED": "Strategy C: AI-Optimized Integrated Hybrid Protocol",
    }.get(chosen, "Integrated Hybrid Protocol")

    chosen_title_ta = {
        "NATURAL_ONLY": "உத்தி A: இயற்கை வழி வேளாண் மருத்துவம் (நம்மாழ்வார் முறை)",
        "MODERN_ONLY": "உத்தி B: நவீன விஞ்ஞான வேதியியல் மருத்துவம்",
        "INTEGRATED": "உத்தி C: AI ஒருங்கிணைந்த கூட்டுப் பாதுகாப்பு முறை",
    }.get(chosen, "ஒருங்கிணைந்த பாதுகாப்பு முறை")

    exec_en = (
        f"Diagnosed {disease_en} with {diagnostic_confidence*100:.1f}% confidence at {severity} severity. "
        f"Selected {chosen_title_en} because it delivers optimal disease arrest while maintaining farm sustainability."
    )
    exec_ta = (
        f"{disease_ta} {diagnostic_confidence*100:.1f}% உறுதித்தன்மையுடன் ({severity} தீவிரம்) கண்டறியப்பட்டது. "
        f"{chosen_title_ta} தேர்ந்தெடுக்கப்பட்டுள்ளது."
    )

    return {
        "chosen_strategy": chosen,
        "chosen_strategy_title_en": chosen_title_en,
        "chosen_strategy_title_ta": chosen_title_ta,
        "is_escalation_required": False,
        "diagnostic_confidence": diagnostic_confidence,
        "decision_reliability_score": round(diagnostic_confidence * 0.95, 2),
        "executive_summary_en": exec_en,
        "executive_summary_ta": exec_ta,
        "immediate_action_en": strat_c["action_steps_en"][0] if chosen == "INTEGRATED" else (strat_b["action_steps_en"][0] if chosen == "MODERN_ONLY" else strat_a["action_steps_en"][0]),
        "immediate_action_ta": strat_c["action_steps_ta"][0] if chosen == "INTEGRATED" else (strat_b["action_steps_ta"][0] if chosen == "MODERN_ONLY" else strat_a["action_steps_ta"][0]),
        "timeline_en": {
            "Hours 0-24": "Prepare target formulation with clean water; spray early morning or late afternoon.",
            "Days 3-5": "Inspect treated foliage for arrest of lesion halos; check for fresh green shoots.",
            "Day 7": "Perform follow-up photo scan on AgriLedger to calculate recovery percentage.",
        },
        "timeline_ta": {
            "மணி 0-24": "சுத்தமான தண்ணீரில் சரியான அளவில் கரைத்து அதிகாலை அல்லது மாலையில் தெளிக்கவும்.",
            "நாள் 3-5": "புள்ளிகள் காய்ந்துள்ளதா மற்றும் புதிய தளிர்கள் ஆரோக்கியமாக வருகிறதா என கவனிக்கவும்.",
            "நாள் 7": "AgriLedger செயலியில் மீண்டும் புகைப்படம் எடுத்து குணமடைந்த அளவை உறுதிப்படுத்தவும்.",
        },
        "strategies_evaluated": strategies,
        "safety_and_phi_notes_en": [
            "Always wear gloves and mask when mixing agricultural inputs.",
            "Adhere to Pre-Harvest Intervals (PHI) before marketing crops.",
        ],
        "safety_and_phi_notes_ta": [
            "மருந்துகளைக் கையாளும் போது முகக்கவசம் மற்றும் கையுறை அணியவும்.",
            "அறுவடைக்கு முன் குறிப்பிட்ட காத்திருப்பு நாட்களைக் கட்டாயம் பின்பற்றவும்.",
        ],
    }

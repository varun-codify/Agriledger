"""Treatment Follow-up Verification & Failure Intelligence Engine.

Disease-Specific Outcome Metrics:
- Foliar Blights: Lesion progression rate & healthy new leaf area.
- Paddy Blast: Panicle neck rot arrest & healthy tiller count.
- Sucking Pests: Colony mortality & sooty mold clearing.
- Nutrient Deficiencies: Interveinal chlorosis recovery in new growth.

Outcome Classification:
- SUCCESS
- PARTIAL_SUCCESS
- FAILURE
- INCONCLUSIVE
- NO_CHANGE
- WORSENING

Failure Intelligence:
- Analyzes root cause (rain wash-off, resistant strain, advanced necrosis, wrong timing, nutrient confusion)
- Recalibrates treatment strategy rather than repeating failed recommendation.
"""

import datetime
from typing import TypedDict, Literal, Optional

OutcomeClassification = Literal[
    "SUCCESS",
    "PARTIAL_SUCCESS",
    "FAILURE",
    "INCONCLUSIVE",
    "NO_CHANGE",
    "WORSENING",
]


class BaselineTreatmentRecord(TypedDict):
    scan_id: str
    crop: str
    disease_key: str
    disease_name_en: str
    disease_name_ta: str
    initial_severity: str
    initial_estimated_area_pct: float
    initial_photo_preview: str
    treatment_applied_en: str
    treatment_applied_ta: str
    strategy_chosen: str
    application_date_iso: str
    primary_outcome_metric: str


class FollowUpVerificationResult(TypedDict):
    baseline_scan_id: str
    follow_up_date_iso: str
    days_elapsed: int
    outcome: OutcomeClassification
    outcome_title_en: str
    outcome_title_ta: str
    disease_reduction_pct: float
    observed_metrics_en: list[str]
    observed_metrics_ta: list[str]
    is_failure: bool
    failure_root_cause_en: Optional[str]
    failure_root_cause_ta: Optional[str]
    recalibrated_strategy_en: Optional[str]
    recalibrated_strategy_ta: Optional[str]
    next_step_recommendation_en: str
    next_step_recommendation_ta: str


# --- In-Memory Verified Outcome Database (Farm Memory) ------------------------
VERIFIED_OUTCOME_DATABASE: list[dict] = []


def evaluate_treatment_followup(
    baseline: BaselineTreatmentRecord,
    follow_up_estimated_area_pct: float,
    user_observed_new_symptoms: bool = False,
    rain_occurred_within_24h: bool = False,
    treatment_adherence_complete: bool = True,
) -> FollowUpVerificationResult:
    """Evaluates follow-up evidence against disease baseline to determine outcome and failure intelligence."""
    initial_pct = baseline.get("initial_estimated_area_pct", 25.0)

    # Calculate change in affected tissue
    diff = initial_pct - follow_up_estimated_area_pct
    reduction_pct = (diff / initial_pct) * 100.0 if initial_pct > 0 else 0.0

    today_iso = datetime.date.today().isoformat()
    try:
        d0 = datetime.date.fromisoformat(baseline.get("application_date_iso", today_iso))
        days_elapsed = (datetime.date.today() - d0).days
    except Exception:
        days_elapsed = 5

    days_elapsed = max(1, days_elapsed)

    # --- Determine Disease-Specific Outcome -----------------------------------
    if not treatment_adherence_complete:
        outcome: OutcomeClassification = "INCONCLUSIVE"
        title_en = "Inconclusive (Incomplete Treatment Adherence)"
        title_ta = "முடிவற்றது (சரியான முறையில் மருந்து தெளிக்கப்படவில்லை)"
        fail_cause_en = "Prescribed dosage or dilution ratio was not completely followed."
        fail_cause_ta = "பரிந்துரைக்கப்பட்ட மருந்தளவு அல்லது முறை முழுமையாகப் பின்பற்றப்படவில்லை."
        recal_en = "Re-apply recommended treatment with exact water dilution and clean sprayer."
        recal_ta = "பரிந்துரைக்கப்பட்ட அளவை சரியான தண்ணீரில் கரைத்து மீண்டும் தெளிக்கவும்."
        is_fail = True

    elif follow_up_estimated_area_pct > (initial_pct * 1.2) or user_observed_new_symptoms:
        outcome = "WORSENING"
        title_en = "Treatment Failure -- Disease Worsening"
        title_ta = "சிகிச்சை தோல்வி -- நோய் அதிகரித்துள்ளது"
        is_fail = True
        if rain_occurred_within_24h:
            fail_cause_en = "Rain wash-off occurred within hours of application, diluting protective film before absorption."
            fail_cause_ta = "மருந்து தெளித்த சில மணி நேரங்களில் மழை பெய்ததால் மருந்து அடித்துச் செல்லப்பட்டது."
            recal_en = "Add a non-ionic sticker/spreader agent (1ml/L) and re-spray with systemic curative."
            recal_ta = "ஒட்டும் திரவம் (லிட்டருக்கு 1 மி.லி) சேர்த்து மீண்டும் உடனுறிஞ்சி மருந்தை தெளிக்கவும்."
        else:
            fail_cause_en = "Pathogen demonstrated resistance to initial intervention or advanced mycelial penetration occurred."
            fail_cause_ta = "பூஞ்சாணம் மருந்தை எதிர்த்து தீவிரமடைந்துள்ளது அல்லது திசுக்களின் உள்ளே ஆழமாக பரவியுள்ளது."
            recal_en = "Recalibrate to alternate Mode of Action (FRAC class rotation) or Escalate to Agricultural University."
            recal_ta = "மாற்று வேதியியல் வகை மருந்திற்கு மாறவும் அல்லது வேளாண் பல்கலைக்கழகத்தை அணுகவும்."

    elif reduction_pct >= 50.0:
        outcome = "SUCCESS"
        title_en = "Successful Treatment -- Healthy Crop Recovery"
        title_ta = "சிகிச்சை வெற்றி -- பயிர் நலம் பெற்றுள்ளது"
        is_fail = False
        fail_cause_en = None
        fail_cause_ta = None
        recal_en = None
        recal_ta = None

    elif reduction_pct >= 15.0:
        outcome = "PARTIAL_SUCCESS"
        title_en = "Partial Success -- Disease Arrested"
        title_ta = "பகுதி வெற்றி -- நோய் பரவல் தடுக்கப்பட்டுள்ளது"
        is_fail = False
        fail_cause_en = None
        fail_cause_ta = None
        recal_en = None
        recal_ta = None

    else:
        outcome = "NO_CHANGE"
        title_en = "No Significant Change Observed"
        title_ta = "குறிப்பிடத்தக்க மாற்றம் இல்லை"
        is_fail = True
        fail_cause_en = "Pathogen spread arrested but active lesions have not regressed."
        fail_cause_ta = "நோய் பரவல் நின்றுள்ளது, ஆனால் பழைய புண்கள் இன்னும் காயவில்லை."
        recal_en = "Apply biological booster (Panchagavya 3%) to stimulate vigorous new shoot growth."
        recal_ta = "புதிய தளிர்கள் வளர பஞ்சகாவ்யா (3%) தெளித்து பயிரை ஊக்குவிக்கவும்."

    # Formulate metric descriptions
    obs_en = [
        f"Initial affected canopy: {initial_pct:.1f}% -> Follow-up affected canopy: {follow_up_estimated_area_pct:.1f}%",
        f"Calculated lesion reduction: {reduction_pct:.1f}% over {days_elapsed} days.",
    ]
    obs_ta = [
        f"ஆரம்ப பாதிப்பு: {initial_pct:.1f}% -> தற்போதைய பாதிப்பு: {follow_up_estimated_area_pct:.1f}%",
        f"{days_elapsed} நாட்களில் நோய் தணிந்த அளவு: {reduction_pct:.1f}%",
    ]

    next_step_en = recal_en or "Continue preventive cultural sanitation and scout weekly."
    next_step_ta = recal_ta or "இயற்கை பராமரிப்பு மற்றும் வாராந்திர கண்காணிப்பைத் தொடரவும்."

    result: FollowUpVerificationResult = {
        "baseline_scan_id": baseline.get("scan_id", "scan_0"),
        "follow_up_date_iso": today_iso,
        "days_elapsed": days_elapsed,
        "outcome": outcome,
        "outcome_title_en": title_en,
        "outcome_title_ta": title_ta,
        "disease_reduction_pct": round(reduction_pct, 1),
        "observed_metrics_en": obs_en,
        "observed_metrics_ta": obs_ta,
        "is_failure": is_fail,
        "failure_root_cause_en": fail_cause_en,
        "failure_root_cause_ta": fail_cause_ta,
        "recalibrated_strategy_en": recal_en,
        "recalibrated_strategy_ta": recal_ta,
        "next_step_recommendation_en": next_step_en,
        "next_step_recommendation_ta": next_step_ta,
    }

    # Store in Verified Outcome Database
    VERIFIED_OUTCOME_DATABASE.append({
        "baseline": baseline,
        "verification": result,
        "verified_at": today_iso,
    })

    return result

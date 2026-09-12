"""Disease-Specific Microclimate Epidemiological Risk Models.

Replaces generic weather rules with disease-specific pathogen biology:
- Temperature curve & degree-hours
- Relative humidity & leaf-wetness duration
- Growth-stage vulnerability
- Historical farm disease pressure & nitrogen excess factor
"""

from typing import TypedDict, Literal
from app.services.agri_ontology import get_ontology_entry

RiskCategory = Literal["LOW", "MODERATE", "HIGH", "VERY HIGH"]


class MicroclimateInputs(TypedDict, total=False):
    temperature_c: float
    relative_humidity_pct: float
    precipitation_mm: float
    leaf_wetness_hours: float
    wind_speed_kmh: float
    growth_stage: str
    excess_nitrogen_applied: bool
    historical_outbreak_count: int
    days_with_favorable_weather: int


class DiseaseRiskOutput(TypedDict):
    disease_key: str
    disease_name_en: str
    disease_name_ta: str
    risk_level: RiskCategory
    risk_score_normalized: float  # 0.0 to 1.0
    primary_risk_factors_en: list[str]
    primary_risk_factors_ta: list[str]
    preventive_cultural_action_en: str
    preventive_cultural_action_ta: str


# --- Individual Pathogen Risk Models ------------------------------------------

def calculate_rice_blast_risk(inputs: MicroclimateInputs) -> DiseaseRiskOutput:
    """Epidemiological risk model for Pyricularia oryzae (Rice Blast)."""
    temp = inputs.get("temperature_c", 25.0)
    rh = inputs.get("relative_humidity_pct", 75.0)
    wet_hours = inputs.get("leaf_wetness_hours", 4.0)
    stage = inputs.get("growth_stage", "Tillering")
    excess_n = inputs.get("excess_nitrogen_applied", False)
    history = inputs.get("historical_outbreak_count", 0)

    score = 0.1
    factors_en = []
    factors_ta = []

    # Temperature suitability: 20-26C optimal for conidial germination
    if 20.0 <= temp <= 26.0:
        score += 0.30
        factors_en.append(f"Optimal blast sporulation temperature ({temp:.1f} deg C)")
        factors_ta.append(f"குலை நோய் வித்துக்கள் உற்பத்திக்கான உகந்த வெப்பநிலை ({temp:.1f} C)")
    elif 18.0 <= temp <= 29.0:
        score += 0.15

    # Relative humidity > 86%
    if rh >= 88.0:
        score += 0.25
        factors_en.append(f"High relative humidity ({rh:.0f}%) promoting spore release")
        factors_ta.append(f"அதிகக் காற்றின் ஈரப்பதம் ({rh:.0f}%) பூஞ்சாண வித்துக்கள் பரவ சாதகம்")
    elif rh >= 80.0:
        score += 0.12

    # Leaf wetness duration
    if wet_hours >= 9.0:
        score += 0.20
        factors_en.append(f"Extended leaf wetness ({wet_hours:.1f} hours) enabling spore penetration")
        factors_ta.append(f"இலைகள் தொடர்ந்து நனைந்திருக்கும் நேரம் ({wet_hours:.1f} மணி நேரம்)")
    elif wet_hours >= 6.0:
        score += 0.10

    # Excess Nitrogen top-dressing
    if excess_n:
        score += 0.15
        factors_en.append("Excessive nitrogen fertilizer causing soft, susceptible vegetative tissue")
        factors_ta.append("அதிக தழைச்சத்து (யூரியா) இடுவதால் பயிர் திசுக்கள் மென்மையாகி எளிதில் பாதிக்கப்படுதல்")

    # High vulnerability growth stages
    if any(s.lower() in stage.lower() for s in ["panicle", "heading", "neck", "flowering"]):
        score += 0.15
        factors_en.append(f"Critical reproductive stage ({stage}) with high neck-blast risk")
        factors_ta.append(f"கதிர் வெளிவரும் மிக முக்கியமான பருவம் ({stage})")

    # Farm history
    if history > 0:
        score += 0.08

    normalized_score = min(1.0, max(0.0, score))

    if normalized_score >= 0.75:
        risk_level: RiskCategory = "VERY HIGH"
    elif normalized_score >= 0.55:
        risk_level = "HIGH"
    elif normalized_score >= 0.35:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    return {
        "disease_key": "paddy_blast",
        "disease_name_en": "Rice Blast",
        "disease_name_ta": "நெல் குலை நோய் / வெப்பு நோய்",
        "risk_level": risk_level,
        "risk_score_normalized": round(normalized_score, 2),
        "primary_risk_factors_en": factors_en or ["Normal microclimatic conditions; low immediate blast risk."],
        "primary_risk_factors_ta": factors_ta or ["சாதாரண தட்பவெப்ப நிலை; உடனடி குலை நோய் ஆபத்து குறைவு."],
        "preventative_cultural_action_en": "Pause nitrogen top-dressing; maintain 3-5cm standing water; spray prophylactic Pseudomonas @ 5g/L.",
        "preventative_cultural_action_ta": "யூரியா இடுவதை தற்காலிகமாக நிறுத்தவும்; வயலில் 3-5 செ.மீ நீர் தேக்கி வைக்கவும்; சூடோமோனாஸ் (லிட்டருக்கு 5 கிராம்) முன்னெச்சரிக்கையாக தெளிக்கவும்.",
    }


def calculate_tomato_early_blight_risk(inputs: MicroclimateInputs) -> DiseaseRiskOutput:
    """Epidemiological risk model for Alternaria solani (Tomato Early Blight)."""
    temp = inputs.get("temperature_c", 26.0)
    rh = inputs.get("relative_humidity_pct", 70.0)
    wet_hours = inputs.get("leaf_wetness_hours", 3.0)
    rain = inputs.get("precipitation_mm", 0.0)
    stage = inputs.get("growth_stage", "Flowering")

    score = 0.1
    factors_en = []
    factors_ta = []

    # Temperature suitability: 24-29C optimal for Alternaria
    if 24.0 <= temp <= 29.0:
        score += 0.30
        factors_en.append(f"Warm daytime temperature ({temp:.1f} deg C) favoring Alternaria growth")
        factors_ta.append(f"ஆல்டர்னேரியா பூஞ்சாணம் வளர்வதற்கான உகந்த வெப்பநிலை ({temp:.1f} C)")
    elif 18.0 <= temp <= 32.0:
        score += 0.15

    # High humidity & Alternating wet/dry cycles
    if rh >= 80.0 or rain > 5.0:
        score += 0.25
        factors_en.append(f"High canopy humidity ({rh:.0f}%) and rainfall creating spore germination splash")
        factors_ta.append(f"அதிகக் காற்றின் ஈரப்பதம் ({rh:.0f}%) மற்றும் மழைநீர் மூலம் வித்துக்கள் பரவுதல்")
    elif rh >= 65.0:
        score += 0.10

    if wet_hours >= 6.0:
        score += 0.20
        factors_en.append(f"Leaf surface wetness ({wet_hours:.1f} hrs) allowing germ tube penetration")
        factors_ta.append(f"இலைப்பரப்பில் நீண்ட நேரம் ஈரம் தங்குதல் ({wet_hours:.1f} மணி நேரம்)")

    # Fruiting / heavy fruit load stage has highest susceptibility
    if any(s.lower() in stage.lower() for s in ["fruiting", "harvest", "flowering"]):
        score += 0.15
        factors_en.append(f"Heavy fruiting stage ({stage}) stressing lower canopy foliage")
        factors_ta.append(f"காய் காய்க்கும் தருணம் ({stage}) அடி இலைகளில் நோய் பரவ சாதகம்")

    normalized_score = min(1.0, max(0.0, score))

    if normalized_score >= 0.75:
        risk_level: RiskCategory = "VERY HIGH"
    elif normalized_score >= 0.55:
        risk_level = "HIGH"
    elif normalized_score >= 0.35:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    return {
        "disease_key": "tomato_early_blight",
        "disease_name_en": "Tomato Early Blight",
        "disease_name_ta": "தக்காளி முன் பருவ இலை கருகல் நோய்",
        "risk_level": risk_level,
        "risk_score_normalized": round(normalized_score, 2),
        "primary_risk_factors_en": factors_en or ["Dry warm conditions; low early blight risk."],
        "primary_risk_factors_ta": factors_ta or ["குறைந்த ஈரப்பதம்; கருகல் நோய் தாக்கும் வாய்ப்பு குறைவு."],
        "preventative_cultural_action_en": "Prune lower 12 inches of foliage; apply straw mulch to prevent soil-splash spores; spray sour buttermilk (5%).",
        "preventative_cultural_action_ta": "நிலத்தில் படும் அடி இலைகளைக் கவாத்து செய்யவும்; வைக்கோல் மூடாக்கு அமைக்கவும்; புளித்த மோர் கரைசல் (5%) தெளிக்கவும்.",
    }


def calculate_coconut_whitefly_risk(inputs: MicroclimateInputs) -> DiseaseRiskOutput:
    """Epidemiological risk model for Aleurodicus rugioperculatus (Spiraling Whitefly)."""
    temp = inputs.get("temperature_c", 30.0)
    rain = inputs.get("precipitation_mm", 0.0)
    wind = inputs.get("wind_speed_kmh", 12.0)

    score = 0.1
    factors_en = []
    factors_ta = []

    # Warm dry weather (28-36C) encourages explosive whitefly reproduction
    if 28.0 <= temp <= 37.0 and rain < 2.0:
        score += 0.35
        factors_en.append(f"Warm dry dry-spell conditions ({temp:.1f} deg C, minimal rain) accelerating whitefly multiplication")
        factors_ta.append(f"மழையற்ற வெப்பமான உலர் வானிலை ({temp:.1f} C) வெள்ளை ஈக்கள் பல்கிப் பெருக சாதகம்")

    # Moderate wind speed disperses adult flies across orchards
    if wind >= 10.0:
        score += 0.20
        factors_en.append(f"Breezy winds ({wind:.0f} km/h) facilitating adult whitefly flight between palms")
        factors_ta.append(f"மிதமான காற்று ({wind:.0f} கி.மீ/மணி) தோட்டங்களுக்கு இடையே ஈக்கள் பரவ உதவுதல்")

    # Low rainfall prevents natural wash-off
    if rain == 0.0:
        score += 0.15
        factors_en.append("Zero rainfall allowing waxy honeydew and black sooty mold accumulation")
        factors_ta.append("மழையின்மை காரணமாக ஓலைகளில் மெழுகு மற்றும் கரும்பூஞ்சாணம் தேங்குதல்")

    normalized_score = min(1.0, max(0.0, score))

    if normalized_score >= 0.70:
        risk_level: RiskCategory = "VERY HIGH"
    elif normalized_score >= 0.50:
        risk_level = "HIGH"
    elif normalized_score >= 0.30:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    return {
        "disease_key": "coconut_whitefly",
        "disease_name_en": "Coconut Spiraling Whitefly & Sooty Mold",
        "disease_name_ta": "தென்னை சுருள் வெள்ளை ஈ மற்றும் கரும்பூஞ்சாணம்",
        "risk_level": risk_level,
        "risk_score_normalized": round(normalized_score, 2),
        "primary_risk_factors_en": factors_en or ["Wet/rainy weather actively dislodging whitefly colonies."],
        "primary_risk_factors_ta": factors_ta or ["மழைக்காலம் வெள்ளை ஈக்களின் எண்ணிக்கையைக் கட்டுப்படுத்துகிறது."],
        "preventative_cultural_action_en": "Install yellow sticky traps (8/acre); spray high-pressure water jet on underside of fronds; preserve Encarsia parasitoids.",
        "preventative_cultural_action_ta": "ஏக்கருக்கு 8 மஞ்சள் ஒட்டும் பொறிகள் கட்டவும்; விசைத்தெளிப்பான் மூலம் தண்ணீர் பீய்ச்சி அடிக்கவும்; இயற்கை என்கார்சியா ஒட்டுண்ணிகளைப் பாதுகாக்கவும்.",
    }


def predict_disease_risk(disease_key: str, inputs: MicroclimateInputs) -> DiseaseRiskOutput:
    """Router to compute pathogen-specific epidemiological risk."""
    if disease_key == "paddy_blast":
        return calculate_rice_blast_risk(inputs)
    elif disease_key == "tomato_early_blight":
        return calculate_tomato_early_blight_risk(inputs)
    elif disease_key == "coconut_whitefly":
        return calculate_coconut_whitefly_risk(inputs)

    # Generic Extensible Pathology Risk Calculator from Ontology
    ontology = get_ontology_entry(disease_key)
    if not ontology:
        return {
            "disease_key": disease_key,
            "disease_name_en": disease_key.replace("_", " ").title(),
            "disease_name_ta": disease_key,
            "risk_level": "LOW",
            "risk_score_normalized": 0.20,
            "primary_risk_factors_en": ["Insufficient specific epidemiological model; low baseline risk."],
            "primary_risk_factors_ta": ["பிரத்யேக மாதிரி இல்லை; பொதுவான ஆபத்து குறைவு."],
            "preventative_cultural_action_en": "Maintain regular farm scouting and balanced irrigation.",
            "preventative_cultural_action_ta": "தொடர் பயிர் கண்காணிப்பு மற்றும் சீரான பாசனத்தைப் பராமரிக்கவும்.",
        }

    env = ontology.get("favorable_environment", {})
    temp = inputs.get("temperature_c", 25.0)
    rh = inputs.get("relative_humidity_pct", 70.0)

    score = 0.1
    factors_en = []
    factors_ta = []

    if env.get("opt_temp_min", 20.0) <= temp <= env.get("opt_temp_max", 30.0):
        score += 0.35
        factors_en.append(f"Temperature ({temp:.1f} deg C) within favorable pathogen range")
        factors_ta.append(f"வெப்பநிலை ({temp:.1f} C) நோய்க்காரணிக்கு சாதகமாக உள்ளது")

    if rh >= env.get("min_rh", 80.0):
        score += 0.35
        factors_en.append(f"High relative humidity ({rh:.0f}%) exceeding pathogen threshold")
        factors_ta.append(f"அதிகக் காற்றின் ஈரப்பதம் ({rh:.0f}%) நோய் பரவ சாதகம்")

    normalized_score = min(1.0, max(0.0, score))
    risk_level: RiskCategory = "HIGH" if normalized_score >= 0.60 else ("MODERATE" if normalized_score >= 0.35 else "LOW")

    return {
        "disease_key": disease_key,
        "disease_name_en": ontology.get("disease_en", disease_key),
        "disease_name_ta": ontology.get("disease_ta", disease_key),
        "risk_level": risk_level,
        "risk_score_normalized": round(normalized_score, 2),
        "primary_risk_factors_en": factors_en or ["Weather conditions within safe thresholds."],
        "primary_risk_factors_ta": factors_ta or ["வானிலை பாதுகாப்பான வரம்பிற்குள் உள்ளது."],
        "preventative_cultural_action_en": "; ".join(ontology.get("preventative_cultural_en", ["Scout fields regularly."])),
        "preventative_cultural_action_ta": "; ".join(ontology.get("preventative_cultural_ta", ["வயலைத் தொடர்ந்து கண்காணிக்கவும்."])),
    }

"""Shared Gemini client helpers.

Provides ``retry_across_models`` so any AI feature (chat, insights, milk-bill
OCR) transparently fails over to an available model when the configured one is
deprecated, blocked for the key, or otherwise unusable.
"""

import json
import logging
import re

from app.config import config

logger = logging.getLogger(__name__)


def extract_json(text: str | None):
    """Parse the first JSON object out of a model response.

    Gemini is asked for ``response_mime_type="application/json"`` but can still
    occasionally wrap the payload or append stray text (a trailing brace, a
    sentence, markdown fences). This finds the first balanced ``{...}`` block
    and parses it, returning ``None`` when nothing parses.
    """
    if not text:
        return None
    stripped = text.strip()
    # Drop markdown code fences if the model wrapped the answer.
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```\s*$", "", stripped)
    try:
        return json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        pass
    # Fall back to the first balanced { ... } block anywhere in the text.
    start = stripped.find("{")
    while start != -1:
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(stripped)):
            ch = stripped[i]
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
            elif ch == '"':
                in_string = not in_string
            elif not in_string:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = stripped[start : i + 1]
                        try:
                            return json.loads(candidate)
                        except (json.JSONDecodeError, ValueError):
                            break
        start = stripped.find("{", start + 1)
    return None


async def retry_across_models(operation, models: list[str] | None = None):
    """Run ``operation(model)`` over candidate models until one succeeds.

    Args:
        operation: An async callable taking a single model-name argument and
            returning the response (or text). May raise on failure.
        models: Optional explicit candidate list (mainly for tests). Defaults to
            ``config.gemini.model_candidates`` (configured model first, then
            fallbacks), so the preferred model is always tried first.

    Returns:
        The first successful result, or ``None`` if every candidate failed.
    """
    candidates = models if models is not None else config.gemini.model_candidates
    last_error: Exception | None = None
    for model in candidates:
        try:
            result = await operation(model)
            if result is not None:
                return result
        except Exception as e:  # noqa: BLE001 - failover is the point
            last_error = e
            # Individual failures are expected during failover — only surface
            # a warning when every candidate has failed.
            logger.debug("Gemini model '%s' failed: %s", model, e)
    if last_error is not None:
        logger.warning(
            "All Gemini models failed (%d tried); last error: %s",
            len(candidates),
            last_error,
        )
    else:
        logger.debug(
            "All Gemini models returned empty results (%d tried)",
            len(candidates),
        )
    return None


async def diagnose_crop_disease(
    image_bytes: bytes, mime_type: str = "image/jpeg"
) -> dict | None:
    """Diagnose plant/crop diseases from leaf, fruit, or stem photos using Gemini Vision.

    Returns structured JSON with crop name, disease name, confidence, symptoms,
    organic remedies, chemical remedies with exact dosage, and preventative advice.
    """
    if not config.gemini.is_configured:
        return None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=config.gemini.api_key)
        prompt = (
            "You are an expert agronomist and plant pathologist acting as a Multimodal AI Explanation & Differential Pathology Engine for Indian/South Asian crops "
            "(Paddy/Rice, Sugarcane, Cotton, Coconut, Tomato, Banana, Maize, Chilli, Groundnut, Pulses, Vegetables, etc.).\n"
            "Examine this plant/leaf/fruit photo and provide a scientifically calibrated diagnosis.\n"
            "CRITICAL RULES:\n"
            "1. DO NOT fabricate arbitrary efficacy percentages for remedies. Use categorical evidence strength ('High', 'Moderate', 'Limited') and expected effectiveness ('High', 'Moderate', 'Low').\n"
            "2. Distinguish PLANT HEALTH SUPPORT / VIGOR vs DISEASE SUPPRESSION vs CURATIVE CLAIMS.\n"
            "3. Provide DIFFERENTIAL DIAGNOSIS: breakdown of possible causes (e.g. Primary Disease vs Nutrient Deficiency vs Abiotic Stress vs Bacterial infection).\n"
            "4. If image quality is poor/blurry/non-crop, assign confidence < 70 so the system can trigger an Expert Escalation Gate.\n"
            "5. Provide authentic Tamil agricultural terminology (தூய தமிழ் விவசாய கலைச்சொற்கள்: பூஞ்சை, பாக்டீரியா, நச்சுயிரி, கருகல் நோய், இலைப்புள்ளி, சாம்பல் நோய், சுருள் வெள்ளை ஈ, பஞ்சகாவ்யா, புளித்த மோர்).\n\n"
            "Respond in STRICT JSON with the following exact schema:\n"
            "{\n"
            '  "crop_name": "Tomato",\n'
            '  "crop_name_en": "Tomato",\n'
            '  "crop_name_ta": "தக்காளி",\n'
            '  "is_plant": true,\n'
            '  "status": "Diseased",\n'
            '  "status_ta": "பூஞ்சாணத் தொற்று உடையது",\n'
            '  "disease_name": "Early Blight (Alternaria solani)",\n'
            '  "disease_name_en": "Early Blight (Alternaria solani)",\n'
            '  "disease_name_ta": "முன் பருவ இலை கருகல் நோய் (பூஞ்சை)",\n'
            '  "suggested_ontology_key": "tomato_early_blight",\n'
            '  "pathogen_type_en": "Fungal Infection (Alternaria solani)",\n'
            '  "pathogen_type_ta": "பூஞ்சாணத் தொற்று (Fungus)",\n'
            '  "scientific_name": "Alternaria solani",\n'
            '  "confidence_percentage": 92,\n'
            '  "severity": "Moderate",\n'
            '  "severity_ta": "மிதமானது",\n'
            '  "affected_canopy_percentage": 25.0,\n'
            '  "spread_risk": "High",\n'
            '  "differential_diagnosis": [\n'
            '    {"cause_en": "Early Blight (Alternaria solani)", "cause_ta": "முன் பருவ இலை கருகல் நோய் (பூஞ்சை)", "probability_pct": 76},\n'
            '    {"cause_en": "Septoria Leaf Spot", "cause_ta": "செப்டோரியா இலைப்புள்ளி நோய்", "probability_pct": 14},\n'
            '    {"cause_en": "Magnesium / Potassium Deficiency", "cause_ta": "மெக்னீசியம் / பொட்டாஷ் ஊட்டச்சத்துக் குறைபாடு", "probability_pct": 7},\n'
            '    {"cause_en": "Abiotic Sunscald", "cause_ta": "வெயில் உக்கிரம் / வெப்பப் பாதிப்பு", "probability_pct": 3}\n'
            '  ],\n'
            '  "symptoms_en": ["Concentric dark brown rings on older lower leaves", "Yellow chlorotic halo around spots"],\n'
            '  "symptoms_ta": ["அடி இலைகளில் வளைய வடிவிலான கரும்பழுப்பு நிறப் புள்ளிகள்", "புள்ளிகளைச் சுற்றி மஞ்சள் வளையம் படர்தல்"],\n'
            '  "traditional_remedies_en": ["Sour Buttermilk Spray (50ml/L fermented 3 days) to form acidic protective barrier", "Panchagavya 3% (30ml/L) foliar spray to stimulate plant vigor", "Neem Seed Kernel Extract (NSKE 5%) or Neem oil 5ml/L to inhibit conidial germination"],\n'
            '  "traditional_remedies_ta": ["புளித்த மோர் கரைசல்: 3 நாட்கள் புளிக்க வைத்த மோர் 50 மி.லி/லிட்டர் தண்ணீரில் கலந்து தெளிக்கவும்", "பஞ்சகாவ்யா கரைசல் 3% (லிட்டருக்கு 30 மி.லி) தெளித்து பயிர் வளர்ச்சியை மீட்கவும்", "வேப்பங்கொட்டை சாறு 5% அல்லது வேப்பெண்ணெய் கரைசல் (லிட்டருக்கு 5 மி.லி) பூஞ்சாண வித்துக்களைக் கட்டுப்படுத்தும்"],\n'
            '  "modern_remedies_en": ["Mancozeb 75% WP @ 2.0 - 2.5 g/L as contact multi-site protectant", "Copper Oxychloride 50% WP @ 2.5 g/L", "Azoxystrobin 23% SC @ 1.0 ml/L for aggressive active spread"],\n'
            '  "modern_remedies_ta": ["மேன்கோசெப் 75% WP: லிட்டருக்கு 2.0 - 2.5 கிராம் கலந்து இலைகளில் நனையும்படி தெளிக்கவும்", "காப்பர் ஆக்ஸிகுளோரைடு 50% WP: லிட்டருக்கு 2.5 கிராம்", "அசாக்ஸிஸ்ட்ரோபின் 23% SC: லிட்டருக்கு 1.0 மி.லி (தீவிர பரவலின் போது)"],\n'
            '  "preventative_measures_en": ["Prune lower 12 inches of foliage after plant reaches 2 feet height to stop soil splash", "Apply straw mulch to suppress rain-splash inocula", "Avoid overhead sprinkler irrigation"],\n'
            '  "preventative_measures_ta": ["செடி 2 அடி வளர்ந்தவுடன் தரைமட்டத்தில் உள்ள அடி இலைகளைக் கவாத்து செய்யவும்", "வைக்கோல் மூடாக்கு அமைத்து மண் தெறிப்பதைத் தவிர்க்கவும்", "சொட்டு நீர் பாசனம் அமைக்கவும்; தெளிப்பு நீர்ப்பாசனத்தை தவிர்க்கவும்"],\n'
            '  "summary_en": "Moderate Early Blight fungal infection detected on lower canopy. Traditional fermented buttermilk spray and Panchagavya recommended; use Mancozeb only if active spread exceeds 10% canopy.",\n'
            '  "summary_ta": "தக்காளி அடி இலைகளில் மிதமான பூஞ்சாணக் கருகல் நோய் கண்டறியப்பட்டுள்ளது. முதலில் பாரம்பரிய புளித்த மோர் மற்றும் பஞ்சகாவ்யா கரைசலைத் தெளிக்கவும்; நோய் தீவிரமடைந்தால் மேன்கோசெப் பயன்படுத்தவும்."\n'
            "}\n"
            "Rules: Return STRICT valid JSON without markdown outside fences. If non-plant, set is_plant=false."
        )

        async def _run_diagnosis(model: str):
            return await client.aio.models.generate_content(
                model=model,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

        response = await retry_across_models(_run_diagnosis)
        if response and response.text:
            return extract_json(response.text)
    except Exception as e:
        logger.exception(f"Crop disease diagnosis failed: {e}")
    return None


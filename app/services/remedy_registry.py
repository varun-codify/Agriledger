"""Remedy Registry & Evidence Engine.

Strictly distinguishes:
- Plant Health Support / Vigor vs Suppression vs Control vs Curative Claim.
- Controlled categorical Evidence Strength (Very High, High, Moderate, Limited, Insufficient).
- Controlled categorical Expected Effectiveness (Very High, High, Moderate, Low, Unknown).
- Failure conditions, limitations, biological compatibility, and regulatory PHI.
"""

from typing import TypedDict, Literal, Optional

EvidenceStrength = Literal["Very High", "High", "Moderate", "Limited", "Insufficient"]
ExpectedEffectiveness = Literal["Very High", "High", "Moderate", "Low", "Unknown"]
RemedyCategory = Literal[
    "botanical_input",
    "fermented_bio_formulation",
    "bio_control_agent",
    "cultural_agronomic",
    "chemical_fungicide",
    "chemical_bactericide",
    "chemical_insecticide",
]
RemedyPurpose = Literal[
    "prevention",
    "plant_vigor",
    "nutrition",
    "suppression",
    "control",
    "recovery_support",
    "curative_only_if_evidence_exists",
]


class RemedyRecord(TypedDict, total=False):
    id: str
    name: str
    name_ta: str
    category: RemedyCategory
    natural_or_modern: Literal["natural", "modern", "biological"]
    target_crops: list[str]
    target_problems: list[str]
    purpose: list[RemedyPurpose]
    application_recipe_en: str
    application_recipe_ta: str
    dilution_rate: str
    compatible_growth_stages: list[str]
    evidence_strength: EvidenceStrength
    expected_effectiveness: ExpectedEffectiveness
    evidence_sources: list[str]
    limitations: list[str]
    failure_conditions: list[str]
    compatibility_notes: str
    safety_phi_days: Optional[int]
    resistance_frac_irac_code: Optional[str]
    estimated_cost_per_acre_inr: float


# --- Registered Remedies Master Catalog ---------------------------------------

REMEDY_REGISTRY: dict[str, RemedyRecord] = {
    # --- NATURAL & BIO FORMULATIONS ------------------------------------------
    "panchagavya_3pct": {
        "id": "panchagavya_3pct",
        "name": "Panchagavya (3% Foliar Spray)",
        "name_ta": "பஞ்சகாவ்யா கரைசல் (3% தெளிப்பு)",
        "category": "fermented_bio_formulation",
        "natural_or_modern": "natural",
        "target_crops": ["Paddy", "Tomato", "Chilli", "Coconut", "Banana", "Vegetables"],
        "target_problems": ["plant_stress", "immunity_induction", "foliar_suppression", "early_blight", "fruit_rot"],
        "purpose": ["plant_vigor", "nutrition", "prevention", "suppression"],
        "application_recipe_en": "Mix 30 ml of well-fermented Panchagavya per 1 liter of water (3% concentration). Spray early morning (6:30-8:30 AM) or evening (4:30-6:00 PM) on foliage.",
        "application_recipe_ta": "1 லிட்டர் தண்ணீருக்கு 30 மி.லி நன்கு நொதித்த பஞ்சகாவ்யா (3%) கலந்து அதிகாலை அல்லது மாலையில் இலைகளில் நன்கு நனையும்படி தெளிக்கவும்.",
        "dilution_rate": "30 ml / Liter (3%)",
        "compatible_growth_stages": ["Vegetative", "Pre-flowering", "Flowering", "Fruit/Grain Filling"],
        "evidence_strength": "High",
        "expected_effectiveness": "Moderate",
        "evidence_sources": [
            "TNAU Agritech Portal Organic Farming Guide (2022)",
            "ICAR-Indian Institute of Farming Systems Research (IIFSR) Technical Bulletin",
            "Nammalvar Natural Farming Ecological Protocols",
        ],
        "limitations": [
            "Not a chemical curative agent; cannot eradicate established deep mycelial fungal tissue necrosis (>20% severity).",
            "Must be prepared with indigenous desi cow inputs (dung, urine, milk, curd, ghee, jaggery, banana, tender coconut) fermented for 21 days with daily stirring.",
        ],
        "failure_conditions": [
            "Rain wash-off within 3 hours of application.",
            "Use during intense midday heat (>35 deg C), which kills beneficial lactic acid and yeast organisms.",
            "Applied to crops under acute late-stage epidemic without integrating barrier controls.",
        ],
        "compatibility_notes": "Compatible with Pseudomonas and Trichoderma; do not mix directly with copper or chemical bactericides in the same tank.",
        "safety_phi_days": 0,
        "resistance_frac_irac_code": "Natural Multimodal / Inducer",
        "estimated_cost_per_acre_inr": 150.0,
    },

    "sour_buttermilk_5pct": {
        "id": "sour_buttermilk_5pct",
        "name": "Fermented Sour Buttermilk Spray (5%)",
        "name_ta": "புளித்த மோர் கரைசல் (5% தெளிப்பு)",
        "category": "fermented_bio_formulation",
        "natural_or_modern": "natural",
        "target_crops": ["Tomato", "Chilli", "Vegetables", "Paddy"],
        "target_problems": ["early_blight", "powdery_mildew", "downy_mildew", "foliar_fungal_spots"],
        "purpose": ["prevention", "suppression", "control"],
        "application_recipe_en": "Ferment 50 ml of sour cow milk buttermilk in a clay pot for 3-4 days until strongly acidic. Mix with 1 liter water and spray on upper and lower leaf surfaces.",
        "application_recipe_ta": "3-4 நாட்கள் மண்பானையில் புளிக்க வைத்த பசும்பால் மோர் 50 மி.லி-ஐ 1 லிட்டர் தண்ணீரில் கலந்து இலைகளின் மேல் மற்றும் கீழ் பகுதியில் தெளிக்கவும்.",
        "dilution_rate": "50 ml / Liter (5%)",
        "compatible_growth_stages": ["Nursery", "Vegetative", "Flowering", "Fruiting"],
        "evidence_strength": "High",
        "expected_effectiveness": "Moderate",
        "evidence_sources": [
            "TNAU Department of Plant Pathology Bio-Input Field Trials",
            "Journal of Organic Agriculture (Bio-Fungicidal properties of lactic acid bacteria)",
        ],
        "limitations": [
            "Suppresses foliar fungal conidia germination via lactic acidity; does not cure systemic vascular wilts.",
        ],
        "failure_conditions": [
            "Using fresh sweet buttermilk instead of fermented sour buttermilk (lacks required low pH <4.2).",
            "High humidity continuous rain washing off lactic acid barrier.",
        ],
        "compatibility_notes": "Do not mix with alkaline ash preparations or chemical copper in the same application.",
        "safety_phi_days": 0,
        "resistance_frac_irac_code": "Acidic Microbiological Barrier",
        "estimated_cost_per_acre_inr": 80.0,
    },

    "neem_oil_formulation_5ml": {
        "id": "neem_oil_formulation_5ml",
        "name": "Cold-Pressed Neem Oil Formulation (0.5%)",
        "name_ta": "தூய வேப்பெண்ணெய் கரைசல் (லிட்டருக்கு 5 மி.லி)",
        "category": "botanical_input",
        "natural_or_modern": "natural",
        "target_crops": ["Coconut", "Tomato", "Chilli", "Paddy", "Cotton", "Vegetables"],
        "target_problems": ["whitefly", "thrips", "aphids", "sooty_mold", "powdery_mildew", "spore_suppression"],
        "purpose": ["prevention", "suppression", "control"],
        "application_recipe_en": "Emulsify 5 ml of pure cold-pressed neem oil with 1 ml khadi/potash liquid soap in 1 liter water (shake vigorously until milky white before spraying).",
        "application_recipe_ta": "1 லிட்டர் தண்ணீரில் 5 மி.லி தூய மரச்செக்கு வேப்பெண்ணெய் மற்றும் 1 மி.லி காதி சோப் திரவம் கலந்து பால் போல் நுரை வரும் வரை குலுக்கி தெளிக்கவும்.",
        "dilution_rate": "5 ml Neem Oil + 1 ml Emulsifier / Liter",
        "compatible_growth_stages": ["All Stages"],
        "evidence_strength": "Very High",
        "expected_effectiveness": "High",
        "evidence_sources": [
            "ICAR-National Research Centre for Integrated Pest Management (NCIPM)",
            "TNAU Insect Toxicology & Plant Pathology Departmental Evaluations",
        ],
        "limitations": [
            "Acts as anti-feedant, oviposition deterrent, and insect growth regulator (IGR); takes 24-48 hours for insect mortality compared to instant chemical knockdowns.",
        ],
        "failure_conditions": [
            "Spraying without soap emulsifier causing oil to float and scorch leaves.",
            "Spraying in harsh hot sunlight (>32 deg C) causing phototoxicity on tender leaves.",
        ],
        "compatibility_notes": "Compatible with most botanical extracts and bio-fungicides; avoid mixing with sulfur sprays.",
        "safety_phi_days": 0,
        "resistance_frac_irac_code": "UN (Botanical IGR & Antifeedant)",
        "estimated_cost_per_acre_inr": 220.0,
    },

    "pseudomonas_fluorescens_bio": {
        "id": "pseudomonas_fluorescens_bio",
        "name": "Pseudomonas fluorescens (TNAU Certified Bio-Agent)",
        "name_ta": "சூடோமோனாஸ் புளோரசன்ஸ் உயிரியல் பூஞ்சாணக் கொல்லி",
        "category": "bio_control_agent",
        "natural_or_modern": "biological",
        "target_crops": ["Paddy", "Tomato", "Chilli", "Banana", "Pulses", "Groundnut"],
        "target_problems": ["paddy_blast", "bacterial_leaf_blight", "damping_off", "fruit_rot", "collar_rot"],
        "purpose": ["prevention", "suppression", "control", "recovery_support"],
        "application_recipe_en": "Mix talc-based Pseudomonas fluorescens (1x10^8 CFU/g) @ 5g/L water (or 1 kg/acre in 200L water) and spray thoroughly on foliage.",
        "application_recipe_ta": "1 லிட்டர் தண்ணீருக்கு 5 கிராம் (ஏக்கருக்கு 1 கிலோ/200 லிட்டர் நீர்) சூடோமோனாஸ் புளோரசன்ஸ் தூள் கலந்து இலைகளில் நன்கு நனையும்படி தெளிக்கவும்.",
        "dilution_rate": "5 g / Liter (Talc formulation)",
        "compatible_growth_stages": ["Seed Treatment", "Nursery Dip", "Tillering", "Flowering"],
        "evidence_strength": "Very High",
        "expected_effectiveness": "High",
        "evidence_sources": [
            "TNAU Agricultural University Pathology Standards",
            "ICAR National Bureau of Agriculturally Important Microorganisms (NBAIM)",
        ],
        "limitations": [
            "Prophylactic bio-shield; optimum when applied before heavy spore incubation. In severe late-stage disease (>25%), requires integration with targeted curatives.",
        ],
        "failure_conditions": [
            "Tank mixing with chemical bactericides (Streptocycline) or Copper fungicides, which instantly kills the living Pseudomonas bacteria.",
            "Using expired powder with CFU count below 10^8.",
        ],
        "compatibility_notes": "CANNOT BE TANK-MIXED with Copper Oxychloride or Streptocycline. Must maintain a 5-7 day gap.",
        "safety_phi_days": 0,
        "resistance_frac_irac_code": "Biological Bio-Antagonist",
        "estimated_cost_per_acre_inr": 180.0,
    },

    # --- MODERN SCIENTIFIC & CIBRC APPROVED REMEDIES -------------------------
    "mancozeb_75wp": {
        "id": "mancozeb_75wp",
        "name": "Mancozeb 75% WP (Contact Protectant Fungicide)",
        "name_ta": "மேன்கோசெப் 75% WP (பூஞ்சாணக் கொல்லி)",
        "category": "chemical_fungicide",
        "natural_or_modern": "modern",
        "target_crops": ["Tomato", "Chilli", "Paddy", "Potato", "Groundnut"],
        "target_problems": ["early_blight", "anthracnose", "fruit_rot", "leaf_spot"],
        "purpose": ["prevention", "control", "curative_only_if_evidence_exists"],
        "application_recipe_en": "Dissolve 2.0 to 2.5 g of Mancozeb 75% WP per liter of water (500g in 200L water per acre). Spray evenly covering both leaf surfaces.",
        "application_recipe_ta": "1 லிட்டர் தண்ணீருக்கு 2.0 முதல் 2.5 கிராம் மேன்கோசெப் (ஏக்கருக்கு 500 கிராம்/200 லிட்டர் நீர்) கலந்து இலைகளின் இருபுறமும் படும்படி தெளிக்கவும்.",
        "dilution_rate": "2.0 - 2.5 g / Liter",
        "compatible_growth_stages": ["Vegetative", "Pre-flowering", "Early Fruiting"],
        "evidence_strength": "Very High",
        "expected_effectiveness": "Very High",
        "evidence_sources": [
            "Central Insecticides Board & Registration Committee (CIBRC) Approved Label Claims",
            "TNAU Crop Protection Guide 2023",
        ],
        "limitations": [
            "Contact multi-site protectant; does not penetrate internally to kill deeply established systemic fungal infections.",
        ],
        "failure_conditions": [
            "Application during heavy downpour without sticker/spreader agent (washes off leaf surface).",
            "Applied after disease has reached >40% canopy collapse.",
        ],
        "compatibility_notes": "Compatible with most neutral insecticides; do not mix with highly alkaline mixtures (e.g. Bordeaux mixture).",
        "safety_phi_days": 5,
        "resistance_frac_irac_code": "FRAC M03 (Multi-site Dithiocarbamate - Low Resistance Risk)",
        "estimated_cost_per_acre_inr": 320.0,
    },

    "tricyclazole_75wp": {
        "id": "tricyclazole_75wp",
        "name": "Tricyclazole 75% WP (Systemic Blast Curative)",
        "name_ta": "டிரைசைக்ளசோல் 75% WP (குலை நோய் பிரத்யேக மருந்து)",
        "category": "chemical_fungicide",
        "natural_or_modern": "modern",
        "target_crops": ["Paddy"],
        "target_problems": ["paddy_blast", "neck_blast", "node_blast"],
        "purpose": ["control", "curative_only_if_evidence_exists"],
        "application_recipe_en": "Dissolve 0.6 g of Tricyclazole 75% WP per liter of water (120g in 200L water per acre) at first appearance of blast lesions or at 5% panicle emergence.",
        "application_recipe_ta": "1 லிட்டர் தண்ணீருக்கு 0.6 கிராம் (ஏக்கருக்கு 120 கிராம்) டிரைசைக்ளசோல் கலந்து குலை நோய் அறிகுறிகள் தெரிந்தவுடன் அல்லது கதிர் வெளிவரும் தருணத்தில் தெளிக்கவும்.",
        "dilution_rate": "0.6 g / Liter",
        "compatible_growth_stages": ["Tillering", "Panicle Initiation", "Booting", "Heading"],
        "evidence_strength": "Very High",
        "expected_effectiveness": "Very High",
        "evidence_sources": [
            "CIBRC Label Claim Standards for Rice Blast",
            "ICAR-National Rice Research Institute (NRRI) Standard Operating Protocols",
            "TNAU Agri-Tech Portal Paddy Recommendations",
        ],
        "limitations": [
            "Specific melanin biosynthesis inhibitor for Pyricularia blast fungus; ineffective against bacterial leaf blight or sheath rot.",
        ],
        "failure_conditions": [
            "Misdiagnosed Bacterial Leaf Blight mistaken for Blast.",
            "Applied more than twice consecutively causing selection of resistant strains.",
        ],
        "compatibility_notes": "Compatible with common rice insecticides like Chlorantraniliprole.",
        "safety_phi_days": 30,
        "resistance_frac_irac_code": "FRAC I1 (Melanin Biosynthesis Inhibitor)",
        "estimated_cost_per_acre_inr": 450.0,
    },

    "copper_oxychloride_50wp": {
        "id": "copper_oxychloride_50wp",
        "name": "Copper Oxychloride 50% WP (Broad-Spectrum Contact)",
        "name_ta": "காப்பர் ஆக்ஸிகுளோரைடு 50% WP (பூஞ்சாணம் மற்றும் பாக்டீரியா கொல்லி)",
        "category": "chemical_fungicide",
        "natural_or_modern": "modern",
        "target_crops": ["Tomato", "Chilli", "Paddy", "Banana", "Vegetables"],
        "target_problems": ["bacterial_leaf_blight", "early_blight", "anthracnose", "fruit_rot", "downy_mildew"],
        "purpose": ["prevention", "control", "curative_only_if_evidence_exists"],
        "application_recipe_en": "Dissolve 2.5 g Copper Oxychloride 50% WP per liter of water (500g in 200L water per acre). Spray thoroughly covering entire plant foliage.",
        "application_recipe_ta": "1 லிட்டர் தண்ணீருக்கு 2.5 கிராம் காப்பர் ஆக்ஸிகுளோரைடு (ஏக்கருக்கு 500 கிராம்) கலந்து செடி முழுவதும் நனையும்படி தெளிக்கவும்.",
        "dilution_rate": "2.5 g / Liter",
        "compatible_growth_stages": ["Vegetative", "Fruiting"],
        "evidence_strength": "Very High",
        "expected_effectiveness": "High",
        "evidence_sources": [
            "CIBRC Approved Product Specifications",
            "TNAU Crop Protection Compendium",
        ],
        "limitations": [
            "Contact inorganic multi-site protectant; do not spray during active peak flowering as high copper can cause flower drop.",
        ],
        "failure_conditions": [
            "Tank mixing with live bio-agents (Trichoderma, Pseudomonas) which kills the micro-organisms.",
        ],
        "compatibility_notes": "DO NOT TANK MIX with bio-agents (Pseudomonas, Trichoderma). Wait at least 7 days between applications.",
        "safety_phi_days": 7,
        "resistance_frac_irac_code": "FRAC M01 (Inorganic Copper - Low Resistance Risk)",
        "estimated_cost_per_acre_inr": 350.0,
    },
}


def get_remedy(remedy_id: str) -> Optional[RemedyRecord]:
    """Retrieve remedy from registry by ID."""
    return REMEDY_REGISTRY.get(remedy_id)


def filter_remedies_for_problem(crop: str, problem_id: str) -> list[RemedyRecord]:
    """Find all matching remedies for a given crop and disease/pest problem."""
    matches = []
    for r in REMEDY_REGISTRY.values():
        crop_match = any(c.lower() in crop.lower() or crop.lower() in c.lower() for c in r.get("target_crops", []))
        prob_match = any(p.lower() in problem_id.lower() or problem_id.lower() in p.lower() for p in r.get("target_problems", []))
        if crop_match and prob_match:
            matches.append(r)
    return matches

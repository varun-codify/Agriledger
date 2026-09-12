"""Formal Agricultural Disease & Crop Health Ontology.

Structured knowledge hierarchy:
Crop -> Disease/Pest/Disorder -> Pathogen -> Type -> Lifecycle -> Symptoms ->
Differential Diagnosis -> Environmental Risk -> Growth-Stage Susceptibility ->
Severity Thresholds -> Strategies (Natural/Biological/Modern/Integrated) -> Resistance Management.
"""

from typing import TypedDict, Literal, Optional

PathogenCategory = Literal[
    "Fungus",
    "Bacteria",
    "Virus",
    "Oomycete",
    "Nematode",
    "Insect Pest",
    "Mite",
    "Nutrient Deficiency",
    "Nutrient Toxicity",
    "Abiotic Stress",
    "Physiological Disorder",
]

SeverityLevel = Literal["None", "Low", "Moderate", "Severe", "Critical"]


class DiseaseOntologyEntry(TypedDict, total=False):
    crop_en: str
    crop_ta: str
    disease_en: str
    disease_ta: str
    pathogen_name: str
    pathogen_category: PathogenCategory
    pathogen_category_ta: str
    transmission_vectors: list[str]
    favorable_environment: dict
    growth_stage_susceptibility: list[str]
    symptoms_en: list[str]
    symptoms_ta: list[str]
    differential_symptoms: list[str]
    severity_indicators: dict[str, str]
    primary_outcome_metric: str
    natural_strategies_en: list[str]
    natural_strategies_ta: list[str]
    biological_strategies_en: list[str]
    biological_strategies_ta: list[str]
    modern_chemical_strategies_en: list[str]
    modern_chemical_strategies_ta: list[str]
    integrated_strategies_en: list[str]
    integrated_strategies_ta: list[str]
    resistance_management_en: list[str]
    resistance_management_ta: list[str]
    preventative_cultural_en: list[str]
    preventative_cultural_ta: list[str]


# --- Comprehensive Disease Knowledge Base -------------------------------------

AGRICULTURAL_ONTOLOGY: dict[str, DiseaseOntologyEntry] = {
    # --- PADDY / RICE ---------------------------------------------------------
    "paddy_blast": {
        "crop_en": "Paddy (Rice)",
        "crop_ta": "நெல்",
        "disease_en": "Rice Blast (Pyricularia oryzae)",
        "disease_ta": "நெல் குலை நோய் / வெப்பு நோய்",
        "pathogen_name": "Magnaporthe oryzae (anamorph Pyricularia oryzae)",
        "pathogen_category": "Fungus",
        "pathogen_category_ta": "பூஞ்சாணம் (Fungus)",
        "transmission_vectors": ["Airborne conidia spores", "Infected seed", "Crop residue"],
        "favorable_environment": {
            "min_temp": 18.0,
            "opt_temp_min": 20.0,
            "opt_temp_max": 26.0,
            "max_temp": 30.0,
            "min_rh": 86.0,
            "min_leaf_wetness_hours": 9,
            "excess_nitrogen_risk": True,
        },
        "growth_stage_susceptibility": ["Nursery", "Tillering", "Panicle Initiation", "Flowering / Neck stage"],
        "symptoms_en": [
            "Spindle-shaped or elliptical eye spots on leaves with ash-gray center and dark brown border",
            "Lesions enlarge and coalesce causing complete leaf desiccation (blast appearance)",
            "Blackish-brown rotting at panicle neck causing chaffy, empty grains (Neck blast)",
            "Nodal rot with lower stem breakage",
        ],
        "symptoms_ta": [
            "இலைகளில் நடுப்பகுதி சாம்பல் நிறமாகவும் ஓரங்கள் கரும்பழுப்பாகவும் உள்ள கண் வடிவ புள்ளிகள்",
            "புள்ளிகள் ஒன்றுசேர்ந்து இலைகள் காய்ந்து தீப்பற்றி வெந்தது போன்ற தோற்றம்",
            "கதிர் கழுத்துப் பகுதியில் கரும்பழுப்பு நிற அழுகல் ஏற்பட்டு தானியங்கள் பதராவது (கழுத்து குலை நோய்)",
            "நெல் தூர்களின் கணுப் பகுதி அழுகி உடைந்து விழுதல்",
        ],
        "differential_symptoms": [
            "Brown Spot spots are small circular/oval without spindle ends",
            "Bacterial Leaf Blight causes wavy yellow-to-white marginal striping starting from leaf tips",
        ],
        "severity_indicators": {
            "Low": "Scattered spindle spots on <5% of lower leaves; no nodal or neck lesions.",
            "Moderate": "Spindle spots on 5-25% foliage; lower tillers showing spots; no neck infection.",
            "Severe": "Coalesced spots on >25% leaf area, collar rot or early neck infection developing.",
            "Critical": "Neck blast on emerging panicles with lodging and >50% crop loss risk.",
        },
        "primary_outcome_metric": "panicle_neck_infection_rate_and_foliar_lesion_spread",
        "natural_strategies_en": [
            "Pseudomonas fluorescens foliar spray @ 5g/L or 2.5 kg/ha in 500L water",
            "Panchagavya 3% foliar spray (30 ml/L of water) in early morning or evening to build systemic acquired resistance",
            "Wood ash dusting (25 kg/acre) during morning dew to form an alkaline protective leaf surface",
            "Cow urine extract (10% solution) mixed with neem leaf decoction to inhibit conidial germination",
        ],
        "natural_strategies_ta": [
            "சூடோமோனாஸ் புளோரசன்ஸ் உயிரியல் பூஞ்சாணக் கொல்லி: லிட்டருக்கு 5 கிராம் (ஏக்கருக்கு 1 கிலோ) தண்ணீரில் கலந்து தெளிக்கவும்",
            "பஞ்சகாவ்யா கரைசல் 3% (லிட்டருக்கு 30 மி.லி) கலந்து அதிகாலை அல்லது மாலையில் தெளித்து பயிரின் நோய் எதிர்ப்பு திறனை கூட்டவும்",
            "அதிகாலை பனி இருக்கும் போது ஏக்கருக்கு 25 கிலோ மரச்சாம்பல் தூவி காரத்தன்மை மூலம் பூஞ்சையை அழிக்கவும்",
            "மாட்டுக்கோமியம் 10% மற்றும் வேப்பிலை சாறு கலவை தெளித்து பூஞ்சாண வித்துக்கள் முளைப்பதை தடுக்கவும்",
        ],
        "biological_strategies_en": [
            "Seed treatment with Trichoderma viride @ 4g/kg seed",
            "Foliar spray of Bacillus subtilis (commercial formulation) @ 3g/L",
        ],
        "biological_strategies_ta": [
            "ட்ரைக்கோடெர்மா விரிடி விதை நேர்த்தி: கிலோ விதைக்கு 4 கிராம்",
            "பேசில்லஸ் சப்டிலிஸ் நுண்ணுயிர் தெளிப்பு: லிட்டருக்கு 3 கிராம்",
        ],
        "modern_chemical_strategies_en": [
            "Tricyclazole 75% WP @ 0.6 g/L (or 120 g/acre) as a curative systemic melanin biosynthesis inhibitor",
            "Isoprothiolane 40% EC @ 1.5 ml/L of water",
            "Kasugamycin 3% SL @ 2.0 ml/L of water for collar and neck blast",
            "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1.0 ml/L during acute epidemic pressure",
        ],
        "modern_chemical_strategies_ta": [
            "டிரைசைக்ளசோல் 75% WP: லிட்டருக்கு 0.6 கிராம் (ஏக்கருக்கு 120 கிராம்) - தீவிர குலை நோய்க்கான நவீன சிகிச்சை",
            "ஐசோப்ரோதியோலேன் 40% EC: லிட்டருக்கு 1.5 மி.லி",
            "காசுகாமைசின் 3% SL: லிட்டருக்கு 2.0 மி.லி (கழுத்து குலை நோய்க்கு சிறந்தது)",
            "அசாக்ஸிஸ்ட்ரோபின் + டைபெனோகோனசோல்: லிட்டருக்கு 1.0 மி.லி",
        ],
        "integrated_strategies_en": [
            "Prophylactic bio-seed treatment + split nitrogen application + Tricyclazole only if lesion area crosses 10% Economic Threshold Level (ETL).",
        ],
        "integrated_strategies_ta": [
            "சூடோமோனாஸ் விதை நேர்த்தி + தழைச்சத்து யூரியாவை பிரித்து இடுதல் + பொருளாதார சேத நிலை (10%) தாண்டினால் மட்டுமே டிரைசைக்ளசோல் தெளித்தல்.",
        ],
        "resistance_management_en": [
            "Do not apply Tricyclazole more than twice in a single season. Alternate with Isoprothiolane or Kasugamycin.",
        ],
        "resistance_management_ta": [
            "டிரைசைக்ளசோல் பூஞ்சாணக் கொல்லியை ஒரு பருவத்தில் இரண்டு முறைக்கு மேல் பயன்படுத்தக் கூடாது; மாற்று மருந்துகளை சுழற்சி முறையில் பயன்படுத்தவும்.",
        ],
        "preventative_cultural_en": [
            "Avoid excessive urea/nitrogen top dressing; split nitrogen into 3-4 doses",
            "Maintain optimal standing water (2-5 cm); do not let field dry completely during blast weather",
            "Burn or deeply plow infected stubbles after harvest",
        ],
        "preventative_cultural_ta": [
            "யூரியாவை ஒரே நேரத்தில் அதிகமாக இடாமல் 3 முதல் 4 தவணைகளாக பிரித்து இடவும்",
            "வயலில் 2-5 செ.மீ நீர் தேக்கி வைக்கவும்; பயிரை வறட்சியில் விடக்கூடாது",
            "அறுவடைக்கு பின் பாதிக்கப்பட்ட தாள்களை தீயிட்டு அல்லது ஆழமாக உழுது அழிக்கவும்",
        ],
    },

    "paddy_blb": {
        "crop_en": "Paddy (Rice)",
        "crop_ta": "நெல்",
        "disease_en": "Bacterial Leaf Blight (Xanthomonas oryzae)",
        "disease_ta": "பாக்டீரியா இலை கருகல் நோய் (வெண் கருகல்)",
        "pathogen_name": "Xanthomonas oryzae pv. oryzae",
        "pathogen_category": "Bacteria",
        "pathogen_category_ta": "பாக்டீரியா (நுண்ணுயிர்)",
        "transmission_vectors": ["Irrigation water", "Rain splash", "Wind-driven rain", "Damaged leaf edges"],
        "favorable_environment": {
            "min_temp": 24.0,
            "opt_temp_min": 26.0,
            "opt_temp_max": 32.0,
            "max_temp": 38.0,
            "min_rh": 85.0,
            "min_leaf_wetness_hours": 8,
            "excess_nitrogen_risk": True,
        },
        "growth_stage_susceptibility": ["Maximum Tillering", "Boot Leaf", "Flowering"],
        "symptoms_en": [
            "Water-soaked translucent stripes starting from leaf tips and margins",
            "Lesions turn wavy, yellow to bleached white along margins with bacterial ooze drops in morning",
            "Kresek phase (seedling wilt) causing whole clump drying and death",
        ],
        "symptoms_ta": [
            "இலை நுனி மற்றும் ஓரங்களில் இருந்து தொடங்கும் நீர் ஊறிய மஞ்சள் நிற அலை அலையான கோடுகள்",
            "பாதிக்கப்பட்ட இலை ஓரங்கள் வெண்மையாக மாறி காய்ந்து போதல்; காலையில் பாக்டீரியா கசிவு திரவம் தோன்றுதல்",
            "கிரசெக் நிலை: நாற்று அல்லது தூர்கள் மொத்தமாக வாடி உலர்ந்து போதல்",
        ],
        "differential_symptoms": [
            "Rice Blast has spindle-shaped spots with gray centers, not wavy marginal bleached stripes",
            "Zinc deficiency causes rusty brown spots across mid-rib without wavy edges",
        ],
        "severity_indicators": {
            "Low": "<5% leaf tip drying, isolated clumps.",
            "Moderate": "5-20% leaf margins bleached, active yellowing.",
            "Severe": ">25% canopy bleached, grain filling impaired.",
            "Critical": "Kresek seedling wilt or extensive flag leaf blight.",
        },
        "primary_outcome_metric": "marginal_bleached_leaf_area_progression",
        "natural_strategies_en": [
            "Fresh cow dung slurry supernatant (20 kg cow dung in 100L water, filtered and sprayed twice at 10-day interval)",
            "Pseudomonas fluorescens @ 5g/L foliar spray",
            "Neem oil 3% (30 ml/L with soap) to restrict bacterial colonization",
        ],
        "natural_strategies_ta": [
            "பசும் சாணக் கரைசல்: 20 கிலோ புதிய சாணத்தை 100 லிட்டர் நீரில் கரைத்து வடிகட்டி 10 நாட்கள் இடைவெளியில் 2 முறை தெளிக்கவும்",
            "சூடோமோனாஸ் புளோரசன்ஸ்: லிட்டருக்கு 5 கிராம் இலைகளில் தெளிக்கவும்",
            "வேப்பெண்ணெய் கரைசல் 3% தெளித்து பாக்டீரியா பரவலைக் கட்டுப்படுத்தவும்",
        ],
        "biological_strategies_en": [
            "Seed treatment with Pseudomonas fluorescens @ 10g/kg seed and seedling dip @ 2.5 kg/ha",
        ],
        "biological_strategies_ta": [
            "சூடோமோனாஸ் விதை நேர்த்தி: கிலோ விதைக்கு 10 கிராம்; நாற்று வேர் நனைத்தல்: ஹெக்டேருக்கு 2.5 கிலோ",
        ],
        "modern_chemical_strategies_en": [
            "Copper Hydroxide 53.8% DF @ 2.0 g/L OR Copper Oxychloride 50% WP @ 2.5 g/L",
            "Streptocycline (Streptomycin sulphate 90% + Tetracycline hydrochloride 10%) @ 0.6 g in 10L water + Copper Oxychloride @ 25g/10L (Use strictly for severe epidemic breakout)",
        ],
        "modern_chemical_strategies_ta": [
            "காப்பர் ஹைட்ராக்சைடு 53.8% DF: லிட்டருக்கு 2.0 கிராம் அல்லது காப்பர் ஆக்ஸிகுளோரைடு: லிட்டருக்கு 2.5 கிராம்",
            "ஸ்ட்ரெப்டோசைக்ளின் 0.6 கிராம் + காப்பர் ஆக்ஸிகுளோரைடு 25 கிராம் (10 லிட்டர் தண்ணீருக்கு) - கடுமையான பரவலுக்கு மட்டும்",
        ],
        "integrated_strategies_en": [
            "Drain excess field water + pause urea application + spray cow dung supernatant or Copper Hydroxide.",
        ],
        "integrated_strategies_ta": [
            "வயலில் தேங்கிய நீரை வடிக்கவும் + யூரியா உரமிடுவதை தற்காலிகமாக நிறுத்தவும் + சாணக்கரைசல் அல்லது காப்பர் ஹைட்ராக்சைடு தெளிக்கவும்.",
        ],
        "resistance_management_en": [
            "Do not use antibiotics repeatedly to prevent bacterial drug resistance.",
        ],
        "resistance_management_ta": [
            "ஸ்ட்ரெப்டோசைக்ளின் போன்ற நுண்ணுயிர் எதிர்ப்பிகளை தொடர்ந்து பயன்படுத்தக் கூடாது.",
        ],
        "preventative_cultural_en": [
            "Drain field water immediately when blight is observed",
            "Do not clip seedling tips during transplanting (entry point for bacteria)",
            "Plant resistant varieties: CO 51, ADT 45, CR 1009 Sub-1",
        ],
        "preventative_cultural_ta": [
            "நோய் கண்டவுடன் வயலில் உள்ள தண்ணீரை உடனடியாக வடித்து விடவும்",
            "நாற்று நடும் போது இலை நுனிகளைக் கிள்ளக்கூடாது (பாக்டீரியா நுழையும் வழி)",
            "நோய் எதிர்ப்பு திறன் கொண்ட ரகங்களைப் பயிரிடவும் (கோ 51, ஏடிடீ 45, சிஆர் 1009)",
        ],
    },

    # --- TOMATO ---------------------------------------------------------------
    "tomato_early_blight": {
        "crop_en": "Tomato",
        "crop_ta": "தக்காளி",
        "disease_en": "Early Blight (Alternaria solani)",
        "disease_ta": "முன் பருவ இலை கருகல் நோய் (பூஞ்சை)",
        "pathogen_name": "Alternaria solani",
        "pathogen_category": "Fungus",
        "pathogen_category_ta": "பூஞ்சாணம் (Fungus)",
        "transmission_vectors": ["Soil splash", "Wind-borne conidia", "Infected crop debris"],
        "favorable_environment": {
            "min_temp": 16.0,
            "opt_temp_min": 24.0,
            "opt_temp_max": 29.0,
            "max_temp": 34.0,
            "min_rh": 80.0,
            "min_leaf_wetness_hours": 6,
            "alternating_wet_dry": True,
        },
        "growth_stage_susceptibility": ["Vegetative (lower foliage)", "Flowering", "Fruiting"],
        "symptoms_en": [
            "Dark brown to black circular lesions on older lower leaves with concentric rings (target-board effect)",
            "Yellow halo (chlorosis) surrounding expanding lesions",
            "Premature leaf drop from the bottom up exposing fruit to sunscald",
            "Sunken dark cankers on stems and dark leathery rot at fruit stem end",
        ],
        "symptoms_ta": [
            "அடி இலைகளில் வளைய வடிவிலான கரும்பழுப்பு நிறப் புள்ளிகள் (இலக்கு பலகை போன்ற தோற்றம்)",
            "புள்ளிகளைச் சுற்றி மஞ்சள் வளையம் படர்தல்",
            "அடி இலைகள் காய்ந்து உதிர்ந்து காய்கள் வெயிலில் வெந்துபோதல்",
            "தண்டுகளில் கரும்பழுப்பு புண்கள் மற்றும் காய்களின் காம்பு பகுதியில் தோல் போன்ற அழுகல்",
        ],
        "differential_symptoms": [
            "Late Blight causes rapidly expanding pale green/water-soaked lesions with white downy fungal mold on underside",
            "Septoria Leaf Spot has numerous tiny (2-3mm) circular spots with grayish-white centers and black pycnidia dots",
        ],
        "severity_indicators": {
            "Low": "Isolated target spots restricted to bottom 1-2 leaf tiers (<5% foliage).",
            "Moderate": "Spots progressing up the middle canopy (5-20% leaf area); lower leaves yellowing.",
            "Severe": ">25% foliage desiccated, defoliation reaching upper canopy, stem cankers present.",
            "Critical": ">50% defoliation and fruit collar rot threatening entire harvest.",
        },
        "primary_outcome_metric": "lower_canopy_defoliation_and_lesion_progression",
        "natural_strategies_en": [
            "Sour Buttermilk Spray: Ferment 50 ml sour buttermilk for 3 days in 1L water; spray weekly to build acidic protective barrier",
            "Neem Seed Kernel Extract (NSKE 5%) or Neem oil (5ml/L + 1ml liquid soap)",
            "Panchagavya 3% (30 ml/L) foliar spray in morning",
            "Trichoderma viride or Pseudomonas fluorescens @ 5g/L foliar spray",
        ],
        "natural_strategies_ta": [
            "புளித்த மோர் கரைசல்: 3 நாட்கள் புளிக்க வைத்த மோர் 50 மி.லி ஒரு லிட்டர் நீரில் கலந்து தெளிக்கவும்",
            "வேப்பங்கொட்டை சாறு 5% அல்லது வேப்பெண்ணெய் கரைசல் (லிட்டருக்கு 5 மி.லி + 1 மி.லி சோப்)",
            "பஞ்சகாவ்யா கரைசல் 3% அதிகாலையில் தெளித்து பயிரின் நோய் எதிர்ப்பு திறனை கூட்டவும்",
            "ட்ரைக்கோடெர்மா விரிடி அல்லது சூடோமோனாஸ்: லிட்டருக்கு 5 கிராம் தெளிக்கவும்",
        ],
        "biological_strategies_en": [
            "Soil drenching with Trichoderma harzianum @ 2.5 kg/acre enriched in 500 kg farmyard manure",
        ],
        "biological_strategies_ta": [
            "மக்கிய தொழுவுரத்துடன் ட்ரைக்கோடெர்மா ஹார்சியானம் (ஏக்கருக்கு 2.5 கிலோ) கலந்து நிலத்தில் இடுதல்",
        ],
        "modern_chemical_strategies_en": [
            "Mancozeb 75% WP @ 2.0 - 2.5 g/L (Contact protectant fungicide; PHI: 5 days)",
            "Copper Oxychloride 50% WP @ 2.5 g/L (Broad-spectrum contact bactericide/fungicide)",
            "Azoxystrobin 23% SC @ 1.0 ml/L (Systemic strobilurin for active aggressive spread)",
            "Chlorothalonil 75% WP @ 2.0 g/L",
        ],
        "modern_chemical_strategies_ta": [
            "மேன்கோசெப் 75% WP: லிட்டருக்கு 2.0 - 2.5 கிராம் (அறுவடைக்கு முன் காத்திருப்பு காலம்: 5 நாட்கள்)",
            "காப்பர் ஆக்ஸிகுளோரைடு 50% WP: லிட்டருக்கு 2.5 கிராம்",
            "அசாக்ஸிஸ்ட்ரோபின் 23% SC: லிட்டருக்கு 1.0 மி.லி (தீவிர பரவலின் போது)",
            "குளோரோதலோனில் 75% WP: லிட்டருக்கு 2.0 கிராம்",
        ],
        "integrated_strategies_en": [
            "Bottom leaf pruning + straw mulching + sour buttermilk spray for mild severity; Mancozeb if disease crosses 10% canopy.",
        ],
        "integrated_strategies_ta": [
            "அடி இலைகளைக் கிள்ளுதல் + வைக்கோல் மூடாக்கு + புளித்த மோர் தெளிப்பு; நோய் 10% இலைப்பரப்பைத் தாண்டினால் மேன்கோசெப் தெளிக்கவும்.",
        ],
        "resistance_management_en": [
            "Alternate Strobilurins (Azoxystrobin) with multi-site contact fungicides (Mancozeb/Chlorothalonil) to prevent resistance.",
        ],
        "resistance_management_ta": [
            "அசாக்ஸிஸ்ட்ரோபின் மருந்தை தொடர்ந்து பயன்படுத்தாமல் மேன்கோசெப் போன்ற மாற்று மருந்துகளுடன் சுழற்சி முறையில் பயன்படுத்தவும்.",
        ],
        "preventative_cultural_en": [
            "Prune lower 12 inches of foliage after plant reaches 2 feet height to avoid soil-splash spores",
            "Apply paddy straw or plastic mulch to suppress rain-splash inocula",
            "Use drip irrigation; never use overhead sprinkler irrigation",
            "Rotate crops with non-solanaceous crops (cereals/pulses) every 2 seasons",
        ],
        "preventative_cultural_ta": [
            "செடி 2 அடி வளர்ந்தவுடன் நிலத்தில் படும் கீழ் 1 அடி இலைகளைக் கவாத்து செய்து அப்புறப்படுத்தவும்",
            "வைக்கோல் மூடாக்கு அமைத்து மண் தெறிப்பதைக் கட்டுப்படுத்தவும்",
            "சொட்டு நீர் பாசனம் அமைக்கவும்; தெளிப்பு நீர் பாசனத்தை தவிர்க்கவும்",
            "பயறு அல்லது தானிய பயிர்களுடன் 2 பருவங்களுக்கு ஒருமுறை பயிர் சுழற்சி செய்யவும்",
        ],
    },

    # --- COCONUT -------------------------------------------------------------
    "coconut_whitefly": {
        "crop_en": "Coconut Palm",
        "crop_ta": "தென்னை",
        "disease_en": "Rugose Spiraling Whitefly & Sooty Mold",
        "disease_ta": "சுருள் வெள்ளை ஈ மற்றும் கரும்பூஞ்சாணம்",
        "pathogen_name": "Aleurodicus rugioperculatus (Pest) + Capnodium spp. (Sooty mold)",
        "pathogen_category": "Insect Pest",
        "pathogen_category_ta": "சாறு உறிஞ்சும் பூச்சி & கரும்பூஞ்சை",
        "transmission_vectors": ["Wind dispersal", "Transport of infested seedlings", "Adult flight"],
        "favorable_environment": {
            "min_temp": 25.0,
            "opt_temp_min": 28.0,
            "opt_temp_max": 35.0,
            "max_temp": 42.0,
            "min_rh": 50.0,
            "dry_hot_spells": True,
        },
        "growth_stage_susceptibility": ["Young palms", "Bearing adult palms"],
        "symptoms_en": [
            "White waxy spiraling egg trails and flocculent waxy powder on the underside of leaflets",
            "Excess honeydew excretion attracting secondary black sooty mold covering upper leaf surface",
            "Blackening of fronds obstructing photosynthesis, resulting in yellowing and reduced nut yield",
        ],
        "symptoms_ta": [
            "ஓலைகளின் அடிப்பகுதியில் வெள்ளை நிற மெழுகு போன்ற சுருள் வடிவ முட்டைப் படிவுகள்",
            "ஈக்கள் வெளியேற்றும் தேன் திரவத்தால் ஓலைகளின் மேற்பகுதியில் கருமை நிற கரும்பூஞ்சாணம் படர்தல்",
            "சூரிய ஒளி கிடைக்காமல் ஒளிச்சேர்க்கை பாதிக்கப்பட்டு ஓலைகள் மஞ்சளாகி மகசூல் குறைதல்",
        ],
        "differential_symptoms": [
            "Coconut scale insects produce yellowish crusted scales without white waxy spiraling deposits",
            "Nutrient deficiency causes uniform golden yellowing of older fronds without black sooty mold",
        ],
        "severity_indicators": {
            "Low": "Spiraling deposits on <10% lower fronds; no black sooty mold.",
            "Moderate": "10-30% fronds covered with wax; patchy black mold on upper fronds.",
            "Severe": ">40% fronds completely blackened with dense whitefly colonies; nut drop beginning.",
            "Critical": "Whole crown blackened with severe photosynthetic impairment.",
        },
        "primary_outcome_metric": "whitefly_colony_reduction_and_sooty_mold_clearance",
        "natural_strategies_en": [
            "High-pressure water jet spraying directed at the underside of leaflets to wash off nymphs, wax, and mold",
            "Neem oil 3% formulation: 30ml pure neem oil + 10g washing soap powder dissolved in 10L water",
            "Yellow Sticky Traps: Install 8-10 large yellow poly-sheets (5x1.5 ft) coated with castor oil per acre",
            "Conservation of natural parasitoid wasp Encarsia guadeloupae (DO NOT spray synthetic insecticides)",
        ],
        "natural_strategies_ta": [
            "விசைத்தெளிப்பான் மூலம் தண்ணீரை வேகமாக பீய்ச்சி அடித்து வெள்ளை ஈக்களையும் கரும்பூஞ்சாணத்தையும் கழுவுதல்",
            "வேப்பெண்ணெய் கரைசல்: 10 லிட்டர் தண்ணீருக்கு 30 மி.லி வேப்பெண்ணெய் + 10 கிராம் சோப்பு தூள் கலந்து மட்டைகளின் அடிப்பகுதியில் தெளிக்கவும்",
            "மஞ்சள் நிற ஒட்டும் பொறிகள்: ஏக்கருக்கு 8 முதல் 10 இடங்களில் ஆமணக்கு எண்ணெய் தடவி கட்டி வெள்ளை ஈக்களைக் கவர்தல்",
            "என்கார்சியா ஒட்டுண்ணி குளவிகளைப் பாதுகாத்தல் (பூச்சிக்கொல்லி மருந்துகளை தவிர்க்கவும்)",
        ],
        "biological_strategies_en": [
            "Release of predator green lacewing bug (Chrysoperla zastrowi sillemi) @ 1000 eggs/acre",
            "Encarsia guadeloupae parasitoid conservation",
        ],
        "biological_strategies_ta": [
            "கிரிசோபெர்லா இரைவிழுங்கி பூச்சிகள் விடுதல்: ஏக்கருக்கு 1000 முட்டைகள்",
            "என்கார்சியா ஒட்டுண்ணி பாதுகாப்பு",
        ],
        "modern_chemical_strategies_en": [
            "CRITICAL CAUTION: Synthetic chemical insecticides (organophosphates/synthetic pyrethroids) are CONTRAINDICATED as they destroy the Encarsia predator population causing super-pest resurgence.",
            "Azadirachtin 1% (10,000 ppm) @ 2.0 ml/L of water if botanical spray is required",
            "Root feeding with Azadirachtin 1% (10ml in 10ml water) in extreme acute outbreaks only",
        ],
        "modern_chemical_strategies_ta": [
            "எச்சரிக்கை: ரசாயன பூச்சிக்கொல்லிகளை தெளிக்கக் கூடாது; அவை நன்மை செய்யும் என்கார்சியா ஒட்டுண்ணிகளை அழித்து ஈக்களின் பெருக்கத்தை அதிகரிக்கும்",
            "அசாடிராக்டின் 1% (10,000 ppm): லிட்டருக்கு 2 மி.லி தண்ணீரில் கலந்து தெளிக்கவும்",
            "வேர் மூலம் உட்செலுத்துதல்: தீவிர நிலையில் 10 மி.லி அசாடிராக்டின் மருந்தை 10 மி.லி தண்ணீருடன் கலந்து வேரில் கட்டவும்",
        ],
        "integrated_strategies_en": [
            "Water jet spray + yellow sticky traps + sunn hemp border crop + neem oil spray. Avoid synthetic chemicals.",
        ],
        "integrated_strategies_ta": [
            "தண்ணீர் பீய்ச்சி அடித்தல் + மஞ்சள் ஒட்டும் பொறி + சணப்பை வரப்பு பயிர் + வேப்பெண்ணெய் தெளிப்பு.",
        ],
        "resistance_management_en": [
            "Rely entirely on biological Encarsia conservation and physical water sprays.",
        ],
        "resistance_management_ta": [
            "ரசாயன பூச்சிக்கொல்லிகளைத் தவிர்த்து இயற்கை ஒட்டுண்ணி முறையைப் பின்பற்றவும்.",
        ],
        "preventative_cultural_en": [
            "Grow border crops like sunn hemp (Crotalaria juncea) or banana to attract beneficial predator insects",
            "Apply balanced nutrition: 1.3 kg Urea + 2.0 kg Super Phosphate + 2.0 kg MOP (Potash) per tree per year",
            "Ensure regular irrigation and avoid water stress in summer",
        ],
        "preventative_cultural_ta": [
            "தோப்பில் வரப்புப் பயிராக சணப்பை பயிரிட்டு நன்மை செய்யும் பொறிவண்டுகளைப் பெருக்கவும்",
            "வருடத்திற்கு மரம் ஒன்றுக்கு 1.3 கிலோ யூரியா, 2 கிலோ சூப்பர் பாஸ்பேட், 2 கிலோ பொட்டாஷ் உரமிடவும்",
            "கோடையில் நீர் பற்றாக்குறை ஏற்படாமல் சீரான பாசனம் வழங்கவும்",
        ],
    },

    # --- CHILLI --------------------------------------------------------------
    "chilli_anthracnose": {
        "crop_en": "Chilli",
        "crop_ta": "மிளகாய்",
        "disease_en": "Anthracnose & Fruit Rot (Dieback)",
        "disease_ta": "பழ அழுகல் மற்றும் நுனிக்கருகல் நோய் (பூஞ்சை)",
        "pathogen_name": "Colletotrichum capsici / Colletotrichum gloeosporioides",
        "pathogen_category": "Fungus",
        "pathogen_category_ta": "பூஞ்சாணம் (Fungus)",
        "transmission_vectors": ["Infected seeds", "Rain splash", "Wind-blown conidia"],
        "favorable_environment": {
            "min_temp": 22.0,
            "opt_temp_min": 27.0,
            "opt_temp_max": 31.0,
            "max_temp": 36.0,
            "min_rh": 80.0,
            "overhead_splash": True,
        },
        "growth_stage_susceptibility": ["Flowering", "Fruit Formation", "Ripening Stage"],
        "symptoms_en": [
            "Dieback: Tender twigs dry from top downwards with white bleached wood and black acervuli dots",
            "Fruit Rot: Sunken circular to elliptical dark blemishes with concentric rings of black spores on ripening fruits",
            "Infected fruits shrivel, bleach straw-colored, and drop prematurely",
        ],
        "symptoms_ta": [
            "நுனிக்கருகல்: குருத்து மற்றும் கிளைகள் நுனியிலிருந்து கீழ்நோக்கி காய்ந்து வெளுத்துப் போதல்",
            "பழ அழுகல்: பழுக்கும் மிளகாய் காய்களில் பள்ளமான வட்ட வடிவ கரும்புள்ளிகள் மற்றும் கருப்பு வித்து வளையங்கள் தோன்றுதல்",
            "பாதிக்கப்பட்ட காய்கள் வைக்கோல் நிறமாக மாறி முன்கூட்டியே உதிர்ந்து போதல்",
        ],
        "differential_symptoms": [
            "Bacterial soft rot turns fruits into a watery foul-smelling mush without concentric black spore rings",
            "Sunscald causes papery white patches exclusively on the sun-exposed side of the fruit",
        ],
        "severity_indicators": {
            "Low": "Isolated dieback on twig tips (<5% branches); <2% fruit blemish.",
            "Moderate": "5-15% twigs affected; scattered fruit rot on ripening pods.",
            "Severe": ">20% dieback and >15% fruit rot destroying marketable harvest.",
            "Critical": "Epidemic dieback with extensive canopy collapse and severe pod drop.",
        },
        "primary_outcome_metric": "fruit_rot_percentage_and_twig_dieback_arrest",
        "natural_strategies_en": [
            "Fermented Ginger-Garlic-Chilli Extract (Agni Astra / 3G extract @ 30ml/L of water)",
            "Panchagavya 3% (30ml/L) spray at flowering and fruit set",
            "Neem oil 5ml/L + 1ml liquid soap to suppress fungal conidia",
            "Pseudomonas fluorescens foliar spray @ 5g/L",
        ],
        "natural_strategies_ta": [
            "இஞ்சி-பூண்டு-பச்சை மிளகாய் கரைசல் (3G கரைசல்): லிட்டருக்கு 30 மி.லி தண்ணீரில் கலந்து தெளிக்கவும்",
            "பஞ்சகாவ்யா 3% பூக்கும் தருணத்திலும் காய் பிடிக்கும் தருணத்திலும் தெளிக்கவும்",
            "வேப்பெண்ணெய் கரைசல் (லிட்டருக்கு 5 மி.லி + 1 மி.லி சோப்)",
            "சூடோமோனாஸ் புளோரசன்ஸ்: லிட்டருக்கு 5 கிராம் தெளிக்கவும்",
        ],
        "biological_strategies_en": [
            "Seed treatment with Trichoderma viride @ 4g/kg seed + Pseudomonas @ 10g/kg",
        ],
        "biological_strategies_ta": [
            "ட்ரைக்கோடெர்மா விரிடி (4 கிராம்/கிலோ) மற்றும் சூடோமோனாஸ் (10 கிராம்/கிலோ) விதை நேர்த்தி",
        ],
        "modern_chemical_strategies_en": [
            "Copper Oxychloride 50% WP @ 2.5 g/L OR Mancozeb 75% WP @ 2.5 g/L",
            "Azoxystrobin 23% SC @ 1.0 ml/L OR Difenoconazole 25% EC @ 0.5 ml/L during active fruit rot",
            "Tebuconazole 25.9% EC @ 1.0 ml/L of water (Curative triazole fungicide)",
        ],
        "modern_chemical_strategies_ta": [
            "காப்பர் ஆக்ஸிகுளோரைடு: லிட்டருக்கு 2.5 கிராம் அல்லது மேன்கோசெப்: லிட்டருக்கு 2.5 கிராம்",
            "டைபெனோகோனசோல் 25% EC: லிட்டருக்கு 0.5 மி.லி அல்லது டெபுகோனசோல்: லிட்டருக்கு 1.0 மி.லி",
        ],
        "integrated_strategies_en": [
            "Prune infected dieback twigs below healthy node + 3G organic extract + Mancozeb if fruit rot exceeds 5%.",
        ],
        "integrated_strategies_ta": [
            "காய்ந்த நுனிக் கிளைகளை ஆரோக்கியமான பகுதி வரை கவாத்து செய்து அகற்றுதல் + 3G கரைசல் + பழ அழுகல் 5% தாண்டினால் மேன்கோசெப் தெளித்தல்.",
        ],
        "resistance_management_en": [
            "Rotate Triazoles (Difenoconazole/Tebuconazole) with multi-site contact protectants (Copper Oxychloride).",
        ],
        "resistance_management_ta": [
            "டெபுகோனசோல் போன்ற மருந்துகளை தொடர்ந்து பயன்படுத்தாமல் காப்பர் ஆக்ஸிகுளோரைடுடன் மாற்றி மாற்றி தெளிக்கவும்.",
        ],
        "preventative_cultural_en": [
            "Collect and destroy ripe rotten fruits from field to eliminate inocula source",
            "Ensure wide spacing (60 x 45 cm) to allow air circulation and quick leaf drying",
            "Avoid excessive overhead irrigation during flowering and fruit ripening",
        ],
        "preventative_cultural_ta": [
            "பாதிக்கப்பட்ட அழுகிய காய்களை சேகரித்து வயலுக்கு வெளியே தீயிட்டு அழிக்கவும்",
            "செடிகளுக்கு இடையே போதிய இடைவெளி (60 x 45 செ.மீ) விட்டு நல்ல காற்றோட்டத்தை பராமரிக்கவும்",
            "பூக்கும் மற்றும் காய்க்கும் தருணத்தில் தெளிப்பு நீர்ப்பாசனத்தை தவிர்க்கவும்",
        ],
    },
}


def get_ontology_entry(disease_key: str) -> Optional[DiseaseOntologyEntry]:
    """Retrieve disease ontology entry by key."""
    return AGRICULTURAL_ONTOLOGY.get(disease_key)


def list_available_diseases() -> list[dict]:
    """Returns catalog of all registered diseases and crops."""
    catalog = []
    for key, entry in AGRICULTURAL_ONTOLOGY.items():
        catalog.append({
            "key": key,
            "crop_en": entry.get("crop_en"),
            "crop_ta": entry.get("crop_ta"),
            "disease_en": entry.get("disease_en"),
            "disease_ta": entry.get("disease_ta"),
            "pathogen_category": entry.get("pathogen_category"),
        })
    return catalog

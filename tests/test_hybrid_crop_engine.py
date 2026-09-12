"""Comprehensive automated test suite for AI-Powered Hybrid Crop Health & Treatment Engine."""

from app.services.agri_ontology import (
    AGRICULTURAL_ONTOLOGY,
    get_ontology_entry,
    list_available_diseases,
)
from app.services.remedy_registry import (
    REMEDY_REGISTRY,
    get_remedy,
    filter_remedies_for_problem,
)
from app.services.disease_risk_models import (
    calculate_rice_blast_risk,
    calculate_tomato_early_blight_risk,
    calculate_coconut_whitefly_risk,
)
from app.services.hybrid_decision_engine import (
    evaluate_natural_modern_compatibility,
    compute_hybrid_treatment_decision,
)
from app.services.treatment_verifier import (
    evaluate_treatment_followup,
    BaselineTreatmentRecord,
)
from app.services.model_registry import (
    get_model_registry_summary,
    get_system_evaluation_metrics_report,
)


class TestAgriDiseaseOntology:
    """Test suite for Agricultural Disease & Pathology Ontology."""

    def test_ontology_contains_major_crops(self):
        assert "paddy_blast" in AGRICULTURAL_ONTOLOGY
        assert "paddy_blb" in AGRICULTURAL_ONTOLOGY
        assert "tomato_early_blight" in AGRICULTURAL_ONTOLOGY
        assert "coconut_whitefly" in AGRICULTURAL_ONTOLOGY
        assert "chilli_anthracnose" in AGRICULTURAL_ONTOLOGY

    def test_ontology_entry_structure(self):
        blast = get_ontology_entry("paddy_blast")
        assert blast is not None
        assert blast["crop_en"] == "Paddy (Rice)"
        assert blast["crop_ta"] == "நெல்"
        assert blast["pathogen_category"] == "Fungus"
        assert len(blast["symptoms_en"]) > 0
        assert len(blast["symptoms_ta"]) > 0
        assert len(blast["natural_strategies_en"]) > 0
        assert len(blast["modern_chemical_strategies_en"]) > 0
        assert "min_temp" in blast["favorable_environment"]

    def test_list_available_diseases(self):
        catalog = list_available_diseases()
        assert len(catalog) >= 4
        keys = [item["key"] for item in catalog]
        assert "tomato_early_blight" in keys


class TestRemedyRegistryAndEvidence:
    """Test suite for categorical evidence remedies without fabricated percentages."""

    def test_remedy_registry_contains_core_remedies(self):
        assert "panchagavya_3pct" in REMEDY_REGISTRY
        assert "sour_buttermilk_5pct" in REMEDY_REGISTRY
        assert "pseudomonas_fluorescens_bio" in REMEDY_REGISTRY
        assert "mancozeb_75wp" in REMEDY_REGISTRY
        assert "tricyclazole_75wp" in REMEDY_REGISTRY

    def test_categorical_evidence_values(self):
        panchagavya = get_remedy("panchagavya_3pct")
        assert panchagavya["evidence_strength"] in ["Very High", "High", "Moderate", "Limited", "Insufficient"]
        assert panchagavya["expected_effectiveness"] in ["Very High", "High", "Moderate", "Low", "Unknown"]
        assert len(panchagavya["failure_conditions"]) > 0
        assert panchagavya["safety_phi_days"] == 0

    def test_filter_remedies_for_problem(self):
        tomato_remedies = filter_remedies_for_problem("Tomato", "early_blight")
        assert len(tomato_remedies) >= 2


class TestPathogenRiskPredictors:
    """Test suite for disease-specific epidemiological microclimate models."""

    def test_rice_blast_high_risk_conditions(self):
        output = calculate_rice_blast_risk({
            "temperature_c": 23.0,
            "relative_humidity_pct": 92.0,
            "leaf_wetness_hours": 11.0,
            "growth_stage": "Panicle Initiation",
            "excess_nitrogen_applied": True,
            "historical_outbreak_count": 2,
        })
        assert output["risk_level"] in ["HIGH", "VERY HIGH"]
        assert output["risk_score_normalized"] >= 0.70
        assert len(output["primary_risk_factors_en"]) >= 3

    def test_rice_blast_low_risk_conditions(self):
        output = calculate_rice_blast_risk({
            "temperature_c": 35.0,
            "relative_humidity_pct": 50.0,
            "leaf_wetness_hours": 1.0,
            "growth_stage": "Vegetative",
            "excess_nitrogen_applied": False,
        })
        assert output["risk_level"] == "LOW"

    def test_tomato_early_blight_risk(self):
        output = calculate_tomato_early_blight_risk({
            "temperature_c": 26.0,
            "relative_humidity_pct": 88.0,
            "leaf_wetness_hours": 8.0,
            "growth_stage": "Fruiting",
        })
        assert output["risk_level"] in ["HIGH", "VERY HIGH"]

    def test_coconut_whitefly_risk(self):
        output = calculate_coconut_whitefly_risk({
            "temperature_c": 32.0,
            "relative_humidity_pct": 50.0,
            "precipitation_mm": 0.0,
            "wind_speed_kmh": 14.0,
        })
        assert output["risk_level"] in ["HIGH", "VERY HIGH"]


class TestHybridDecisionEngine:
    """Test suite for multi-factor decision logic & escalation gates."""

    def test_low_confidence_triggers_escalation(self):
        decision = compute_hybrid_treatment_decision(
            crop="Tomato",
            disease_key="tomato_early_blight",
            diagnostic_confidence=0.55,  # < 0.70 threshold
            severity="Moderate",
        )
        assert decision["chosen_strategy"] == "EXPERT_ESCALATION"
        assert decision["is_escalation_required"] is True

    def test_low_severity_triggers_monitoring(self):
        decision = compute_hybrid_treatment_decision(
            crop="Tomato",
            disease_key="tomato_early_blight",
            diagnostic_confidence=0.90,
            severity="Low",
            spread_risk="Low",
        )
        assert decision["chosen_strategy"] == "MONITOR_ONLY"
        assert decision["is_escalation_required"] is False

    def test_moderate_severity_triggers_integrated(self):
        decision = compute_hybrid_treatment_decision(
            crop="Tomato",
            disease_key="tomato_early_blight",
            diagnostic_confidence=0.92,
            severity="Moderate",
            spread_risk="High",
        )
        assert decision["chosen_strategy"] == "INTEGRATED"
        assert len(decision["strategies_evaluated"]) >= 3

    def test_biological_compatibility_contraindication(self):
        status, note_en, _ = evaluate_natural_modern_compatibility(
            "Pseudomonas fluorescens bio-fungicide",
            "Copper Oxychloride 50% WP chemical spray",
        )
        assert status == "CONTRAINDICATED"
        assert "destroys beneficial microbes" in note_en


class TestFollowUpVerificationAndFailureRecalibration:
    """Test suite for closed-loop follow-up verification & root cause recalibration."""

    def test_successful_recovery_evaluation(self):
        baseline: BaselineTreatmentRecord = {
            "scan_id": "scan_101",
            "crop": "Tomato",
            "disease_key": "tomato_early_blight",
            "disease_name_en": "Early Blight",
            "disease_name_ta": "முன் பருவ இலை கருகல் நோய்",
            "initial_severity": "Moderate",
            "initial_estimated_area_pct": 30.0,
            "initial_photo_preview": "",
            "treatment_applied_en": "Sour Buttermilk 5% + Mancozeb",
            "treatment_applied_ta": "புளித்த மோர் + மேன்கோசெப்",
            "strategy_chosen": "INTEGRATED",
            "application_date_iso": "2026-08-14",
            "primary_outcome_metric": "foliar_lesion_spread",
        }
        res = evaluate_treatment_followup(
            baseline=baseline,
            follow_up_estimated_area_pct=10.0,  # 66.7% reduction
            user_observed_new_symptoms=False,
            rain_occurred_within_24h=False,
        )
        assert res["outcome"] == "SUCCESS"
        assert res["is_failure"] is False
        assert res["disease_reduction_pct"] > 50.0

    def test_rain_washoff_failure_recalibration(self):
        baseline: BaselineTreatmentRecord = {
            "scan_id": "scan_102",
            "crop": "Tomato",
            "disease_key": "tomato_early_blight",
            "disease_name_en": "Early Blight",
            "disease_name_ta": "முன் பருவ இலை கருகல் நோய்",
            "initial_severity": "Moderate",
            "initial_estimated_area_pct": 20.0,
            "initial_photo_preview": "",
            "treatment_applied_en": "Mancozeb 75% WP",
            "treatment_applied_ta": "மேன்கோசெப்",
            "strategy_chosen": "MODERN_ONLY",
            "application_date_iso": "2026-08-14",
            "primary_outcome_metric": "foliar_lesion_spread",
        }
        res = evaluate_treatment_followup(
            baseline=baseline,
            follow_up_estimated_area_pct=28.0,  # Worsened
            user_observed_new_symptoms=True,
            rain_occurred_within_24h=True,
        )
        assert res["outcome"] == "WORSENING"
        assert res["is_failure"] is True
        assert "Rain wash-off" in str(res["failure_root_cause_en"])
        assert "sticker/spreader" in str(res["recalibrated_strategy_en"])


class TestModelRegistryAndGovernance:
    """Test suite for research audit trail and model governance."""

    def test_model_registry_contains_models(self):
        models = get_model_registry_summary()
        assert len(models) >= 2
        assert models[0]["deployment_status"] == "PRODUCTION"

    def test_evaluation_metrics_report_separation(self):
        report = get_system_evaluation_metrics_report()
        assert "diagnostic_performance" in report
        assert "risk_prediction_performance" in report
        assert "treatment_appropriateness_performance" in report
        assert report["leakage_safeguards_active"] is True

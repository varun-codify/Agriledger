"""Tests for AI Crop Disease Diagnostic Scanner."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


from app.database import crud
from app.services.gemini_service import diagnose_crop_disease
from app.states.disease_scanner_state import DiseaseScannerState


def _run(coro):
    return asyncio.run(coro)


# --- Service Tests -----------------------------------------------------

def test_diagnose_crop_disease_no_key_returns_none():
    mock_config = MagicMock()
    mock_config.gemini.is_configured = False
    with patch("app.services.gemini_service.config", mock_config):
        res = _run(diagnose_crop_disease(b"fake-image-bytes"))
        assert res is None


def test_diagnose_crop_disease_success_parsing():
    sample_response = MagicMock()
    sample_response.text = '''{
        "crop_name": "Tomato",
        "is_plant": true,
        "status": "Diseased",
        "disease_name": "Early Blight",
        "scientific_name": "Alternaria solani",
        "confidence_percentage": 96,
        "severity": "Moderate",
        "symptoms": ["Concentric dark spots"],
        "organic_remedies": ["Neem oil 5ml/L"],
        "chemical_remedies": ["Mancozeb 2.5g/L"],
        "preventative_measures": ["Avoid overhead irrigation"],
        "summary": "Early Blight detected."
    }'''

    mock_config = MagicMock()
    mock_config.gemini.is_configured = True
    mock_config.gemini.api_key = "test-key"

    with patch("app.services.gemini_service.config", mock_config), patch(
        "app.services.gemini_service.retry_across_models", new=AsyncMock(return_value=sample_response)
    ):
        result = _run(diagnose_crop_disease(b"valid-image", mime_type="image/jpeg"))
        assert result is not None
        assert result["crop_name"] == "Tomato"
        assert result["disease_name"] == "Early Blight"
        assert result["confidence_percentage"] == 96
        assert len(result["organic_remedies"]) > 0


def test_disease_scanner_state_tab_and_clear():
    state = DiseaseScannerState()
    assert state.remedy_tab in ["hybrid", "traditional"]
    
    state.set_remedy_tab("modern")
    assert state.remedy_tab == "modern"
    
    state.set_language("ta")
    assert state.language == "ta"
    assert state.is_tamil is True
    
    state.current_diagnosis = {
        "crop_name_en": "Tomato",
        "crop_name_ta": "தக்காளி",
        "disease_name_en": "Early Blight",
        "disease_name_ta": "முன் பருவ இலை கருகல் நோய்",
        "traditional_remedies_ta": ["புளித்த மோர் கரைசல் 50 மி.லி/லிட்டர்"],
        "modern_remedies_ta": ["மேன்கோசெப் 2.5 கிராம்/லிட்டர்"],
        "severity_ta": "மிதமானது",
    }
    assert state.display_crop_name == "தக்காளி"
    assert state.display_disease_name == "முன் பருவ இலை கருகல் நோய்"
    assert len(state.display_traditional_remedies) == 1
    assert "புளித்த மோர்" in state.display_traditional_remedies[0]
    
    state.set_language("en")
    assert state.display_crop_name == "Tomato"
    assert state.display_disease_name == "Early Blight"
    
    state.image_preview = "data:image/jpeg;base64,123"
    state.clear_scan()
    assert state.current_diagnosis == {}
    assert state.image_preview == ""


def test_handle_image_upload_with_fallback():
    state = DiseaseScannerState()
    mock_upload_file = MagicMock()
    mock_upload_file.read = AsyncMock(return_value=b"test-leaf-image-data")
    mock_upload_file.content_type = "image/jpeg"

    # When Gemini returns None, it falls back to ontology diagnostic templates
    with patch("app.states.disease_scanner_state.diagnose_crop_disease", new=AsyncMock(return_value=None)):
        _run(state.handle_image_upload([mock_upload_file]))
        assert state.is_scanning is False
        assert state.current_diagnosis != {}
        assert "crop_name" in state.current_diagnosis
        assert "disease_name" in state.current_diagnosis
        assert len(state.scan_history) == 1
        assert state.image_preview.startswith("data:image/jpeg;base64,")


def test_save_diagnosis_to_crop():
    state = DiseaseScannerState()
    state.current_diagnosis = {
        "disease_name": "Rice Blast",
        "severity": "Severe",
        "summary": "Blast detected on paddy crop.",
    }
    state.selected_crop_id = "crop-101"

    auth_mock = MagicMock()
    auth_mock.farm_id = "farm-123"

    crop_state_mock = MagicMock()
    crop_state_mock.crops_list = [
        {"id": "crop-101", "name": "Paddy", "field_name": "North Field", "activities": []}
    ]

    with patch.object(DiseaseScannerState, "get_state", new=AsyncMock(side_effect=[auth_mock, crop_state_mock])), patch.object(
        crud, "update_crop", new=AsyncMock(return_value=True)
    ) as update_mock:
        _run(state.save_diagnosis_to_crop())
        assert state.saved_to_records is True
        update_mock.assert_awaited_once()
        args = update_mock.await_args.args
        assert args[0] == "crop-101"
        assert len(args[1]["activities"]) == 1
        assert "Rice Blast" in args[1]["activities"][0]["notes"]

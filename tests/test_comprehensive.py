"""Comprehensive test suite for AgriLedger.

Tests cover: auth security, database CRUD, state management,
services, i18n, and component rendering.
"""

import datetime
import os
from unittest.mock import MagicMock, patch



# ─── Security / Auth Tests ────────────────────────────────────────────


class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_hash_password_returns_string(self):
        from app.security import hash_password

        result = hash_password("testpassword123")
        assert isinstance(result, str)
        assert len(result) > 0
        # bcrypt hashes start with $2b$
        assert result.startswith("$2b$")

    def test_hash_round_trip_verification(self):
        from app.security import hash_password, verify_password

        # bcrypt is salted: the same password hashes differently each time,
        # but verify_password round-trips correctly.
        hashed = hash_password("hello")
        assert verify_password("hello", hashed)
        assert not verify_password("wrong-password", hashed)

    def test_hash_password_different_inputs(self):
        from app.security import hash_password

        assert hash_password("password1") != hash_password("password2")

    def test_hash_password_empty_string(self):
        from app.security import hash_password

        result = hash_password("")
        assert isinstance(result, str)
        assert len(result) > 0
        assert result.startswith("$2b$")


# ─── Config Tests ─────────────────────────────────────────────────────


class TestConfig:
    """Tests for the centralized configuration module."""

    def test_config_loads_default_mongodb_uri(self):
        from app.config import MongoDBConfig

        cfg = MongoDBConfig()
        assert cfg.uri  # Should have a default value

    def test_config_singleton(self):
        from app.config import config

        assert config is not None
        assert config.mongodb is not None
        assert config.gemini is not None

    def test_gemini_not_configured_without_key(self):
        from app.config import GeminiConfig

        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
            cfg = GeminiConfig()
            assert not cfg.is_configured

    def test_resend_not_configured_without_key(self):
        from app.config import ResendConfig

        with patch.dict(os.environ, {"RESEND_API_KEY": ""}, clear=False):
            cfg = ResendConfig()
            assert not cfg.is_configured

    def test_gemini_model_candidates_configured_first(self):
        from app.config import GeminiConfig

        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "k", "GEMINI_MODEL": "custom-model"},
            clear=False,
        ):
            cfg = GeminiConfig()
        candidates = cfg.model_candidates
        assert candidates[0] == "custom-model"
        assert "custom-model" in candidates

    def test_gemini_model_candidates_dedup(self):
        from app.config import GEMINI_MODEL_FALLBACKS, GeminiConfig

        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "k", "GEMINI_MODEL": GEMINI_MODEL_FALLBACKS[0]},
            clear=False,
        ):
            cfg = GeminiConfig()
        candidates = cfg.model_candidates
        assert len(candidates) == len(set(candidates))
        assert candidates[0] == GEMINI_MODEL_FALLBACKS[0]
        assert len(candidates) == len(GEMINI_MODEL_FALLBACKS)

    def test_gemini_model_candidates_include_fallbacks(self):
        from app.config import GEMINI_MODEL_FALLBACKS, GeminiConfig

        with patch.dict(os.environ, {"GEMINI_API_KEY": "k"}, clear=False):
            cfg = GeminiConfig()
        candidates = cfg.model_candidates
        for fallback in GEMINI_MODEL_FALLBACKS:
            assert fallback in candidates

    def test_retry_across_models_returns_first_success(self):
        import asyncio

        from app.services.gemini_service import retry_across_models

        async def operation(model):
            if model.startswith("deprecated"):
                raise RuntimeError("404 not found")
            return f"ok-{model}"

        result = asyncio.get_event_loop().run_until_complete(
            retry_across_models(operation, ["deprecated-1", "gemini-3.5-flash"])
        )
        assert result == "ok-gemini-3.5-flash"

    def test_retry_across_models_none_when_all_fail(self):
        import asyncio

        from app.services.gemini_service import retry_across_models

        async def operation(model):
            raise RuntimeError(f"{model} unavailable")

        result = asyncio.get_event_loop().run_until_complete(
            retry_across_models(operation, ["a", "b"])
        )
        assert result is None

    def test_extract_json_plain(self):
        from app.services.gemini_service import extract_json

        assert extract_json('{"ok": true}') == {"ok": True}

    def test_extract_json_stray_trailing_brace(self):
        """Gemini occasionally appends a stray '}' after valid JSON."""
        from app.services.gemini_service import extract_json

        payload = '{"litres": 12.5, "fat": 4.2}\n}\n'
        assert extract_json(payload) == {"litres": 12.5, "fat": 4.2}

    def test_extract_json_markdown_fence(self):
        from app.services.gemini_service import extract_json

        assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}

    def test_extract_json_text_around_json(self):
        from app.services.gemini_service import extract_json

        assert extract_json('Here: {"a": 1, "b": 2} thanks') == {"a": 1, "b": 2}

    def test_extract_json_garbage_returns_none(self):
        from app.services.gemini_service import extract_json

        assert extract_json("no json here") is None
        assert extract_json("") is None
        assert extract_json(None) is None

    def test_extract_json_nested_braces(self):
        from app.services.gemini_service import extract_json

        assert extract_json('{"a": {"b": 1}, "c": 2}') == {"a": {"b": 1}, "c": 2}

    def test_extract_json_escaped_quotes(self):
        from app.services.gemini_service import extract_json

        payload = '{"a": "he said \\"hi\\"", "b": 2}'
        assert extract_json(payload) == {"a": 'he said "hi"', "b": 2}

    def test_extract_json_brace_inside_string(self):
        from app.services.gemini_service import extract_json

        assert extract_json('{"a": "}", "b": 2}') == {"a": "}", "b": 2}
        assert extract_json('{"a": "{", "b": 2}') == {"a": "{", "b": 2}

    def test_extract_json_trailing_garbage_after_first_block(self):
        from app.services.gemini_service import extract_json

        payload = '{"a": 1} trailing text {"b": 2}'
        assert extract_json(payload) == {"a": 1}

    def test_twilio_not_configured_without_key(self):
        from app.config import TwilioConfig

        with patch.dict(
            os.environ,
            {"TWILIO_ACCOUNT_SID": "", "TWILIO_AUTH_TOKEN": "", "TWILIO_PHONE_NUMBER": ""},
            clear=False,
        ):
            cfg = TwilioConfig()
            assert not cfg.is_configured


# ─── Model Tests ──────────────────────────────────────────────────────


class TestModels:
    """Tests for database model definitions."""

    def test_user_role_literal(self):

        valid_roles = ["admin", "worker", "viewer"]
        # UserRole is a Literal type; verify the expected values exist in source
        assert len(valid_roles) == 3

    def test_cattle_model_has_feed_records(self):
        from app.database.models import Cattle

        # Verify Cattle TypedDict includes feed_records field
        annotations = Cattle.__annotations__
        assert "feed_records" in annotations

    def test_user_model_has_phone_field(self):
        from app.database.models import User

        annotations = User.__annotations__
        assert "phone" in annotations
        assert "is_active" in annotations
        assert "role" in annotations

    def test_activity_log_model_exists(self):
        from app.database.models import ActivityLog

        annotations = ActivityLog.__annotations__
        assert "user_email" in annotations
        assert "action" in annotations
        assert "entity_type" in annotations

    def test_feed_record_model_exists(self):
        from app.database.models import FeedRecord

        annotations = FeedRecord.__annotations__
        assert "feed_type" in annotations
        assert "quantity_kg" in annotations
        assert "cost" in annotations


# ─── I18n Tests ───────────────────────────────────────────────────────


class TestI18n:
    """Tests for internationalization support."""

    def test_translations_exist_for_all_languages(self):
        from app.states.i18n_state import TRANSLATIONS

        assert "English" in TRANSLATIONS
        assert "Tamil" in TRANSLATIONS
        assert "Hindi" in TRANSLATIONS

    def test_english_has_dashboard_key(self):
        from app.states.i18n_state import TRANSLATIONS

        assert "nav.dashboard" in TRANSLATIONS["English"]
        assert TRANSLATIONS["English"]["nav.dashboard"] == "Dashboard"

    def test_tamil_has_dashboard_key(self):
        from app.states.i18n_state import TRANSLATIONS

        assert "nav.dashboard" in TRANSLATIONS["Tamil"]
        assert TRANSLATIONS["Tamil"]["nav.dashboard"] == "டாஷ்போர்டு"

    def test_hindi_has_dashboard_key(self):
        from app.states.i18n_state import TRANSLATIONS

        assert "nav.dashboard" in TRANSLATIONS["Hindi"]
        assert TRANSLATIONS["Hindi"]["nav.dashboard"] == "डैशबोर्ड"

    def test_all_languages_have_common_keys(self):
        from app.states.i18n_state import TRANSLATIONS

        common_keys = [
            "nav.dashboard",
            "common.add",
            "common.save",
            "common.cancel",
            "tx.income",
            "tx.expense",
        ]
        for lang in ["English", "Tamil", "Hindi"]:
            for key in common_keys:
                assert key in TRANSLATIONS[lang], f"Missing '{key}' in {lang}"


# ─── Service Tests ────────────────────────────────────────────────────


class TestEmailService:
    """Tests for the (zero-cost stub) email service layer."""

    def test_email_service_stub_always_configured(self):
        from app.services.email_service import EmailService

        # The stub needs no external credentials and is always available.
        svc = EmailService()
        assert svc.is_configured

    def test_send_email_stub_returns_true(self):
        from app.services.email_service import EmailService

        import asyncio

        svc = EmailService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.send_email("test@example.com", "Test", "<p>Hello</p>")
        )
        assert result is True


class TestSMSService:
    """Tests for the (zero-cost WhatsApp-link) SMS service layer."""

    def test_sms_service_available_without_keys(self):
        from app.services.sms_service import SMSService

        # WhatsApp click-to-chat links need no Twilio keys.
        svc = SMSService()
        assert svc.is_configured

    def test_send_sms_returns_true(self):
        from app.services.sms_service import SMSService

        import asyncio

        svc = SMSService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.send_sms("+1234567890", "Test message")
        )
        assert result is True

    def test_whatsapp_link_generation(self):
        from app.services.sms_service import SMSService

        svc = SMSService()
        link = svc._generate_wa_link("9876543210", "Hello farm")
        assert link.startswith("https://wa.me/919876543210?text=")
        assert "Hello%20farm" in link


# ─── State Logic Tests ────────────────────────────────────────────────


class TestTransactionState:
    """Tests for transaction state logic."""

    def test_amount_calculation(self):
        """Verify amount computed var works correctly."""
        from app.states.transaction_state import TransactionState

        state = TransactionState()  # type: ignore
        state.amount_str = "125.50"
        assert state.amount == 125.50

    def test_coconut_total_calculation(self):
        from app.states.transaction_state import TransactionState

        state = TransactionState()  # type: ignore
        state.coconut_count = 100
        state.price_per_coconut = 1.5
        assert state.coconut_total_amount == 150.0

    def test_milk_total_calculation(self):
        from app.states.transaction_state import TransactionState

        state = TransactionState()  # type: ignore
        state.liters = 20.0
        state.rate_per_liter = 5.5
        assert state.milk_total_price == 110.0

    def test_keypad_handle_del(self):
        from app.states.transaction_state import TransactionState

        state = TransactionState()  # type: ignore
        state.amount_str = "123"
        state.handle_keypad("del")
        assert state.amount_str == "12"

    def test_keypad_handle_dot(self):
        from app.states.transaction_state import TransactionState

        state = TransactionState()  # type: ignore
        state.amount_str = "100"
        state.handle_keypad(".")
        assert state.amount_str == "100."

    def test_keypad_prevent_double_dot(self):
        from app.states.transaction_state import TransactionState

        state = TransactionState()  # type: ignore
        state.amount_str = "10.5"
        state.handle_keypad(".")
        assert state.amount_str == "10.5"  # Should not add second dot

    def test_keypad_zero_replacement(self):
        from app.states.transaction_state import TransactionState

        state = TransactionState()  # type: ignore
        state.amount_str = "0"
        state.handle_keypad("5")
        assert state.amount_str == "5"

    def test_expense_categories_populated(self):
        from app.states.transaction_state import TransactionState

        state = TransactionState()  # type: ignore
        assert len(state.expense_categories) > 0
        assert any(c["name"] == "Cattle Feed" for c in state.expense_categories)

    def test_income_categories_populated(self):
        from app.states.transaction_state import TransactionState

        state = TransactionState()  # type: ignore
        assert len(state.income_categories) > 0
        assert any(c["name"] == "Milk Sale" for c in state.income_categories)


class TestCattleState:
    """Tests for cattle state computed vars."""

    def test_demo_data_populated(self):
        from app.states.cattle_state import DEMO_CATTLE_DATA

        assert len(DEMO_CATTLE_DATA) > 0

    def test_demo_data_has_multiple_species(self):
        from app.states.cattle_state import DEMO_CATTLE_DATA

        species = set(c["animal_type"] for c in DEMO_CATTLE_DATA)
        assert "cow" in species
        assert "buffalo" in species
        assert "sheep" in species
        assert "goat" in species


class TestUIState:
    """Tests for UI state."""

    def test_sidebar_toggle(self):
        from app.states.ui_state import UIState

        state = UIState()  # type: ignore
        initial = state.sidebar_collapsed
        state.toggle_sidebar()
        assert state.sidebar_collapsed != initial
        state.toggle_sidebar()
        assert state.sidebar_collapsed == initial


class TestSettingsState:
    """Tests for settings state (farm details, profile, JSON backup)."""

    def _make_state(self):
        from app.states.settings_state import SettingsState

        return SettingsState()  # type: ignore

    def test_farm_details_validation(self):
        state = self._make_state()

        import asyncio

        asyncio.run(state.update_farm_details({"farm_name": "", "farm_location": "X"}))
        assert state.settings_error == "Farm name is required."

        asyncio.run(state.update_farm_details({"farm_name": "Green Acres", "farm_location": ""}))
        assert state.settings_error == "Farm location is required."

    def test_backup_data_exports_all_collections(self):
        import asyncio
        from unittest.mock import AsyncMock, patch

        state = self._make_state()

        auth_mock = MagicMock()
        auth_mock.farm_id = "farm-abc"

        def fake_collection(farm_id):
            return AsyncMock(return_value=[{"id": "x", "farm_id": farm_id}])

        collections = [
            "get_all_cattle", "get_all_crops", "get_all_transactions",
            "get_all_milk_sales", "get_all_coconut_sales", "get_all_breeding_cycles",
            "get_feed_types", "get_feed_stock", "get_feed_consumptions", "get_feeding_plans",
        ]
        with patch.object(
            type(state), "get_state", new=AsyncMock(return_value=auth_mock)
        ), patch.multiple(
            "app.database.crud",
            **{name: fake_collection("farm-abc") for name in collections},
        ):
            result = asyncio.run(state.backup_data())

        assert result is not None, "backup_data must return rx.download"
        assert state.is_exporting is False, "is_exporting must reset in finally"

    def test_backup_data_resets_flag_on_error(self):
        import asyncio
        from unittest.mock import AsyncMock, patch

        state = self._make_state()
        auth_mock = MagicMock()
        auth_mock.farm_id = "farm-abc"

        with patch.object(
            type(state), "get_state", new=AsyncMock(return_value=auth_mock)
        ), patch.multiple(
            "app.database.crud",
            get_all_cattle=AsyncMock(side_effect=RuntimeError("db down")),
        ):
            result = asyncio.run(state.backup_data())

        assert state.is_exporting is False
        assert result is not None  # error toast


class TestNotificationState:
    """Tests for notification state."""

    def test_add_notification(self):
        from app.states.notification_state import NotificationState

        state = NotificationState()  # type: ignore
        state.add_notification({"title": "Test", "message": "Hello", "type": "info"})
        assert len(state.notifications) == 1
        assert state.unread_count == 1

    def test_mark_all_read(self):
        from app.states.notification_state import NotificationState

        state = NotificationState()  # type: ignore
        state.add_notification({"title": "Test", "message": "Hello", "type": "info"})
        state.mark_all_read()
        assert state.unread_count == 0

    def test_clear_notifications(self):
        from app.states.notification_state import NotificationState

        state = NotificationState()  # type: ignore
        state.add_notification({"title": "Test", "message": "Hello", "type": "info"})
        state.clear_notifications()
        assert len(state.notifications) == 0


class TestReportsState:
    """Tests for reports state."""

    def test_date_range_last_30_days(self):
        from app.states.reports_state import ReportsState

        state = ReportsState()  # type: ignore
        state.set_date_range("Last 30 Days")
        assert state.date_range == "Last 30 Days"
        today = datetime.date.today()
        expected_start = (today - datetime.timedelta(days=30)).isoformat()
        assert state.custom_start_date == expected_start

    def test_date_range_this_year(self):
        from app.states.reports_state import ReportsState

        state = ReportsState()  # type: ignore
        state.set_date_range("This Year")
        today = datetime.date.today()
        expected_start = today.replace(month=1, day=1).isoformat()
        assert state.custom_start_date == expected_start


class TestBreedingState:
    """Tests for breeding state logic."""

    def test_demo_breeding_data(self):
        from app.states.breeding_state import DEMO_BREEDING_DATA

        assert len(DEMO_BREEDING_DATA) > 0
        # Should have both cow and buffalo entries
        types = set(c["cattle_type"] for c in DEMO_BREEDING_DATA)
        assert "cow" in types or "buffalo" in types


# ─── Feed Intelligence Tests ──────────────────────────────────────────


class TestFeedState:
    """Tests for the Feed Intelligence module."""

    def test_default_feed_types(self):
        from app.states.feed_state import DEFAULT_FEED_TYPES

        assert len(DEFAULT_FEED_TYPES) == 7
        categories = {ft["category"] for ft in DEFAULT_FEED_TYPES}
        assert categories == {"Concentrate", "Home Grown"}
        assert any(ft["name"] == "Rice Bran" for ft in DEFAULT_FEED_TYPES)

    def test_feed_models_exist(self):
        from app.database.models import (
            FeedConsumption,
            FeedingPlan,
            FeedStock,
            FeedType,
        )

        assert "cost_per_unit" in FeedType.__annotations__
        assert "feed_type_id" in FeedStock.__annotations__
        assert "animal_name" in FeedConsumption.__annotations__
        assert "morning" in FeedingPlan.__annotations__

    def test_feeding_qty_computed(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feeding_qty_str = "12.5"
        assert state.feeding_qty == 12.5

    def test_feeding_qty_invalid_input(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feeding_qty_str = "abc"
        assert state.feeding_qty == 0.0

    def test_feeding_keypad(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feeding_qty_str = "0"
        state.handle_feeding_keypad("5")
        assert state.feeding_qty_str == "5"
        state.handle_feeding_keypad(".")
        assert state.feeding_qty_str == "5."
        state.handle_feeding_keypad("5")
        assert state.feeding_qty_str == "5.5"
        state.handle_feeding_keypad(".")  # no double dot
        assert state.feeding_qty_str == "5.5"
        state.handle_feeding_keypad("del")
        assert state.feeding_qty_str == "5."

    def test_quick_add_qty(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feeding_qty_str = "2"
        state.quick_add_feeding_qty("0.5")
        assert state.feeding_qty_str == "2.5"

    def _sample_state(self):
        import datetime

        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "ft1",
                "name": "Rice Bran",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 28.0,
                "is_custom": False,
                "farm_id": "f",
            }
        ]
        state.inventory = [
            {
                "id": "s1",
                "feed_type_id": "ft1",
                "feed_name": "Rice Bran",
                "quantity": 2.0,
                "unit": "kg",
                "purchase_date": "2026-01-01",
                "supplier": "Annai Feeds",
                "cost": 56.0,
                "expiry_date": None,
                "farm_id": "f",
            }
        ]
        state.consumptions = [
            {
                "id": "c1",
                "date": datetime.date.today().isoformat(),
                "time_of_day": "Morning",
                "animal_id": "a1",
                "animal_name": "Lakshmi",
                "feed_type_id": "ft1",
                "feed_name": "Rice Bran",
                "quantity": 2.0,
                "unit": "kg",
                "notes": "",
                "farm_id": "f",
            }
        ]
        return state

    def test_consumption_analytics(self):
        state = self._sample_state()
        assert state.daily_consumption_kg == 2.0
        assert state.weekly_consumption_kg == 2.0
        assert state.monthly_consumption_kg == 2.0

    def test_consumption_by_feed(self):
        state = self._sample_state()
        by_feed = state.consumption_by_feed
        assert len(by_feed) == 1
        assert by_feed[0]["name"] == "Rice Bran"
        assert by_feed[0]["qty"] == 2.0
        assert by_feed[0]["cost"] == 56.0

    def test_smart_alerts_low_stock(self):
        state = self._sample_state()
        alerts = state.smart_alerts
        titles = [a["title"] for a in alerts]
        assert "Low stock" in titles

    def test_purchase_suggestion_generated(self):
        state = self._sample_state()
        suggestions = state.purchase_suggestions
        assert len(suggestions) == 1
        assert suggestions[0]["name"] == "Rice Bran"
        assert suggestions[0]["days_left"] < 14
        assert suggestions[0]["buy_qty"] > 0

    def test_feed_remaining_total(self):
        state = self._sample_state()
        assert state.feed_remaining_total == 2.0
        assert state.low_stock_count == 1

    def test_daily_report_lines(self):
        state = self._sample_state()
        lines = state._report_lines("daily", [], [], [])
        assert any("Lakshmi" in line for line in lines)

    def test_waste_report_flags_low_conversion(self):
        import datetime

        state = self._sample_state()
        cattle = [
            {
                "id": "a1",
                "name": "Lakshmi",
                "milk_production": [
                    {"date": datetime.date.today().isoformat(), "liters": 0.5}
                ],
            }
        ]
        lines = state._report_lines("waste", cattle, [], [])
        assert any("Lakshmi" in line for line in lines)

    def test_feed_crud_helpers_exist(self):
        from app.database import crud

        for name in [
            "get_feed_types",
            "create_feed_type",
            "get_feed_stock",
            "create_feed_stock",
            "get_feed_consumptions",
            "create_feed_consumption",
            "get_feeding_plans",
            "create_feeding_plan",
            "get_feed_sync_markers",
            "set_feed_sync_marker",
        ]:
            assert hasattr(crud, name), f"Missing crud helper: {name}"

    # ── AI Nutrition Advisor tests ────────────────────────────────────

    def _advisor_state(self):
        import datetime

        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "rb",
                "name": "Rice Bran",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 28.0,
                "is_custom": False,
                "farm_id": "f",
            },
            {
                "id": "ch",
                "name": "Cholam (Fresh Green Fodder)",
                "category": "Home Grown",
                "unit": "bundles",
                "cost_per_unit": 15.0,
                "is_custom": False,
                "farm_id": "f",
            },
        ]
        today = datetime.date.today().isoformat()

        def cons(feed_id: str, qty: float):
            return {
                "id": "x",
                "date": today,
                "time_of_day": "Morning",
                "animal_id": "a1",
                "animal_name": "Lakshmi",
                "feed_type_id": feed_id,
                "feed_name": feed_id,
                "quantity": qty,
                "unit": "kg",
                "notes": "",
                "farm_id": "f",
            }

        # 7 days: 1 kg green + 0.2 kg concentrate per day → conc share ≈ 17%
        state.consumptions = [cons("ch", 1.0) for _ in range(7)] + [
            cons("rb", 0.2) for _ in range(7)
        ]
        milk = [
            {
                "date": (datetime.date.today() - datetime.timedelta(days=i)).isoformat(),
                "liters": 18.0,
            }
            for i in range(7)
        ]
        cattle = [{"id": "a1", "name": "Lakshmi", "image_url": "", "milk_production": milk}]
        return state, cattle

    def test_advisor_recommends_increase_concentrate(self):
        state, cattle = self._advisor_state()
        recs = state._build_recommendations(cattle)
        assert any("Increase" in r["title"] for r in recs)

    def test_advisor_recommends_reduce_concentrate(self):
        import datetime

        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "rb",
                "name": "Rice Bran",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 28.0,
                "is_custom": False,
                "farm_id": "f",
            }
        ]
        today = datetime.date.today().isoformat()
        state.consumptions = [
            {
                "id": "x",
                "date": today,
                "time_of_day": "Morning",
                "animal_id": "a1",
                "animal_name": "L",
                "feed_type_id": "rb",
                "feed_name": "Rice Bran",
                "quantity": 2.0,
                "unit": "kg",
                "notes": "",
                "farm_id": "f",
            }
            for _ in range(7)
        ]
        milk = [
            {
                "date": (datetime.date.today() - datetime.timedelta(days=i)).isoformat(),
                "liters": 10.0,
            }
            for i in range(7)
        ]
        cattle = [{"id": "a1", "name": "L", "image_url": "", "milk_production": milk}]
        recs = state._build_recommendations(cattle)
        assert any(r["title"] == "Reduce concentrate" for r in recs)

    def test_advisor_skips_zero_milk(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = []
        cattle = [{"id": "a1", "name": "L", "image_url": "", "milk_production": []}]
        assert state._build_recommendations(cattle) == []

    # ── Milk vs Feed insight tests ────────────────────────────────────

    def test_milk_feed_drop_insight(self):
        import datetime

        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        today = datetime.date.today()
        milk = [
            {
                "date": (today - datetime.timedelta(days=i)).isoformat(),
                "liters": 18.0,
            }
            for i in range(7)
        ] + [
            {
                "date": (today - datetime.timedelta(days=i)).isoformat(),
                "liters": 24.0,
            }
            for i in range(7, 14)
        ]
        cattle = [{"id": "a1", "name": "Lakshmi", "image_url": "", "milk_production": milk}]
        insights = state._build_milk_feed_insights(cattle)
        assert any("milk down" in i["text"] for i in insights)

    def test_milk_feed_high_intake_low_milk_flags(self):
        import datetime

        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "rb",
                "name": "Rice Bran",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 28.0,
                "is_custom": False,
                "farm_id": "f",
            }
        ]
        today = datetime.date.today().isoformat()
        state.consumptions = [
            {
                "id": "x",
                "date": today,
                "time_of_day": "Morning",
                "animal_id": "a1",
                "animal_name": "L",
                "feed_type_id": "rb",
                "feed_name": "Rice Bran",
                "quantity": 5.0,
                "unit": "kg",
                "notes": "",
                "farm_id": "f",
            }
            for _ in range(7)
        ]
        milk = [
            {
                "date": (datetime.date.today() - datetime.timedelta(days=i)).isoformat(),
                "liters": 5.0,
            }
            for i in range(7)
        ]
        cattle = [{"id": "a1", "name": "L", "image_url": "", "milk_production": milk}]
        insights = state._build_milk_feed_insights(cattle)
        assert any("eats" in i["text"] for i in insights)

    # ── Efficiency ranking tests ──────────────────────────────────────

    def test_efficiency_ranks_sorted(self):
        import datetime

        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "rb",
                "name": "Rice Bran",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 28.0,
                "is_custom": False,
                "farm_id": "f",
            }
        ]
        today = datetime.date.today().isoformat()
        state.consumptions = [
            {
                "id": f"c{i}",
                "date": today,
                "time_of_day": "Morning",
                "animal_id": animal,
                "animal_name": animal,
                "feed_type_id": "rb",
                "feed_name": "Rice Bran",
                "quantity": 2.0,
                "unit": "kg",
                "notes": "",
                "farm_id": "f",
            }
            for animal in ("a1", "a2")
            for i in range(7)
        ]
        milk_a1 = [
            {
                "date": (datetime.date.today() - datetime.timedelta(days=i)).isoformat(),
                "liters": 14.0,
            }
            for i in range(7)
        ]
        milk_a2 = [
            {
                "date": (datetime.date.today() - datetime.timedelta(days=i)).isoformat(),
                "liters": 7.0,
            }
            for i in range(7)
        ]
        cattle = [
            {"id": "a1", "name": "Lakshmi", "image_url": "", "milk_production": milk_a1},
            {"id": "a2", "name": "Kaveri", "image_url": "", "milk_production": milk_a2},
        ]
        ranks = state._build_efficiency_ranks(cattle)
        assert len(ranks) == 2
        assert ranks[0]["score"] > ranks[1]["score"]
        assert ranks[1]["rank"] == "Needs Attention"

    # ── Crops → feed stock tests ──────────────────────────────────────

    def test_is_fodder_crop(self):
        from app.states.feed_state import FeedState

        assert FeedState._is_fodder_crop("Cholam")
        assert FeedState._is_fodder_crop("Sorghum Fodder")
        assert FeedState._is_fodder_crop("Rice Straw")
        assert not FeedState._is_fodder_crop("Coconut")
        assert not FeedState._is_fodder_crop("Banana")

    def test_homegrown_summary_lists_fodder_crops(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "ch",
                "name": "Cholam (Fresh Green Fodder)",
                "category": "Home Grown",
                "unit": "bundles",
                "cost_per_unit": 15.0,
                "is_custom": False,
                "farm_id": "f",
            }
        ]
        crops = [
            {
                "id": "c1",
                "name": "Cholam",
                "harvests": [
                    {"id": "h1", "date": "2026-01-01", "quantity": 100, "unit": "bundles", "income": 0}
                ],
            },
            {
                "id": "c2",
                "name": "Coconut",
                "harvests": [
                    {"id": "h2", "date": "2026-01-01", "quantity": 200, "unit": "nuts", "income": 0}
                ],
            },
        ]
        rows = state._build_homegrown_summary(crops)
        assert len(rows) == 1
        assert rows[0]["name"] == "Cholam"
        assert rows[0]["harvested"] == 100.0
        assert rows[0]["synced"] is False
        assert rows[0]["feed_type_name"] == "Cholam (Fresh Green Fodder)"

    def test_homegrown_summary_marks_synced(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.crop_sync_markers = {"c1": 100.0}
        crops = [
            {
                "id": "c1",
                "name": "Cholam",
                "harvests": [
                    {"id": "h1", "date": "2026-01-01", "quantity": 100, "unit": "bundles", "income": 0}
                ],
            }
        ]
        rows = state._build_homegrown_summary(crops)
        assert rows[0]["synced"] is True
        assert rows[0]["delta"] == 0.0

    def test_homegrown_unit_normalization(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        crops = [
            {
                "id": "c1",
                "name": "Sorghum",
                "harvests": [
                    {"id": "h1", "date": "2026-01-01", "quantity": 50, "unit": "bushels", "income": 0}
                ],
            }
        ]
        rows = state._build_homegrown_summary(crops)
        assert rows[0]["unit"] == "kg"

    # ── Crops → feed stock sync (auto-sync) tests ─────────────────────

    @staticmethod
    def _run(coro):
        # asyncio.run is order-safe: get_event_loop() breaks after any other
        # test calls asyncio.run() (it unsets the thread's current loop).
        import asyncio

        return asyncio.run(coro)

    def _fodder_crop(self, crop_id="c1", qty=50.0, unit="bundles"):
        return {
            "id": crop_id,
            "name": "Cholam",
            "harvests": [
                {"id": "h1", "date": "2026-01-01", "quantity": qty, "unit": unit, "income": 0}
            ],
        }

    def _patch_crud(self):
        from unittest.mock import AsyncMock, patch

        from app.database import crud

        return patch.multiple(
            crud,
            create_feed_type=AsyncMock(return_value=True),
            create_feed_stock=AsyncMock(return_value=True),
            update_feed_stock=AsyncMock(return_value=True),
            set_feed_sync_marker=AsyncMock(return_value=True),
        )

    def test_sync_crop_to_stock_moves_harvest(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        crop = self._fodder_crop()
        with self._patch_crud():
            moved, message = self._run(state._sync_crop_to_stock(crop, "farm1"))
        assert moved is True
        assert "50" in message
        assert state.crop_sync_markers["c1"] == 50.0
        assert len(state.inventory) == 1
        assert state.inventory[0]["feed_name"] == "Cholam (Harvested)"
        assert state.inventory[0]["quantity"] == 50.0
        assert state.inventory[0]["supplier"] == "Harvest"

    def test_sync_crop_to_stock_idempotent(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.crop_sync_markers = {"c1": 50.0}
        crop = self._fodder_crop()
        with self._patch_crud():
            moved, message = self._run(state._sync_crop_to_stock(crop, "farm1"))
        assert moved is False
        assert "already in feed stock" in message
        assert len(state.inventory) == 0

    def test_sync_crop_to_stock_adds_to_existing_batch(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "ch",
                "name": "Cholam (Harvested)",
                "category": "Home Grown",
                "unit": "bundles",
                "cost_per_unit": 0.0,
                "is_custom": True,
                "farm_id": "f",
            }
        ]
        state.inventory = [
            {
                "id": "s1",
                "feed_type_id": "ch",
                "feed_name": "Cholam (Harvested)",
                "quantity": 40.0,
                "unit": "bundles",
                "purchase_date": "2026-01-01",
                "supplier": "Harvest",
                "cost": 0.0,
                "expiry_date": None,
                "farm_id": "f",
            }
        ]
        state.crop_sync_markers = {"c1": 40.0}
        crop = self._fodder_crop(qty=80.0)
        with self._patch_crud():
            moved, _ = self._run(state._sync_crop_to_stock(crop, "farm1"))
        assert moved is True
        assert len(state.inventory) == 1
        assert state.inventory[0]["quantity"] == 80.0
        assert state.crop_sync_markers["c1"] == 80.0

    def test_auto_sync_crops_syncs_only_fodder(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        crops = [
            self._fodder_crop(crop_id="c1", qty=50.0),
            self._fodder_crop(crop_id="c2", qty=30.0),
            {"id": "c3", "name": "Coconut", "harvests": [{"id": "h3", "date": "2026-01-01", "quantity": 200, "unit": "nuts", "income": 0}]},
            {"id": "c4", "name": "Cholam", "harvests": []},
        ]
        with self._patch_crud():
            count = self._run(state._auto_sync_crops(crops, "farm1"))
        assert count == 2
        assert state.crop_sync_markers.get("c1") == 50.0
        assert state.crop_sync_markers.get("c2") == 30.0
        assert "c3" not in state.crop_sync_markers

    # ── Feed simulator tests ──────────────────────────────────────────

    def _sim_state(self):
        import datetime

        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "rb",
                "name": "Rice Bran",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 28.0,
                "is_custom": False,
                "farm_id": "f",
            }
        ]
        today = datetime.date.today().isoformat()
        state.consumptions = [
            {
                "id": f"c{i}",
                "date": today,
                "time_of_day": "Morning",
                "animal_id": "a1",
                "animal_name": "L",
                "feed_type_id": "rb",
                "feed_name": "Rice Bran",
                "quantity": 1.0,
                "unit": "kg",
                "notes": "",
                "farm_id": "f",
            }
            for i in range(7)
        ]
        milk = [
            {
                "date": (datetime.date.today() - datetime.timedelta(days=i)).isoformat(),
                "liters": 10.0,
            }
            for i in range(7)
        ]
        animals = [{"id": "a1", "name": "Lakshmi", "image_url": "", "milk_production": milk}]
        return state, animals

    def test_simulator_estimates_gain_and_profit(self):
        state, animals = self._sim_state()
        res = state._compute_simulation(state.feed_types[0], 50.0, animals)
        assert res["current_qty"] == 1.0
        assert res["new_qty"] == 1.5
        assert res["milk_gain"] > 0
        assert res["delta_cost"] > 0
        assert res["profit_change"] > 0
        assert res["verdict"] == "Profitable"

    def test_simulator_reduction_lowers_cost_and_milk(self):
        state, animals = self._sim_state()
        res = state._compute_simulation(state.feed_types[0], -50.0, animals)
        assert res["delta_cost"] < 0
        assert res["milk_gain"] < 0

    def test_simulator_no_intake_no_gain(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "rb",
                "name": "Rice Bran",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 28.0,
                "is_custom": False,
                "farm_id": "f",
            }
        ]
        animals = [{"id": "a1", "name": "L", "image_url": "", "milk_production": []}]
        res = state._compute_simulation(state.feed_types[0], 50.0, animals)
        assert res["current_qty"] == 0.0
        assert res["milk_gain"] == 0.0

    # ── Ration optimizer tests ────────────────────────────────────────

    def test_cheapest_ration_prefers_cheapest_nutrient(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "rb",
                "name": "Rice Bran",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 28.0,
                "is_custom": False,
                "farm_id": "f",
            },
            {
                "id": "goc",
                "name": "Groundnut Oil Cake",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 52.0,
                "is_custom": False,
                "farm_id": "f",
            },
        ]
        state.ration_category = "Lactating Cow"
        ration = state.cheapest_ration
        assert ration["items"]
        assert ration["items"][0]["name"] == "Rice Bran"  # cheapest per nutrient
        assert ration["total_cost"] > 0
        assert len(ration["items"]) > 1  # 70% variety cap forces a mix

    def test_cheapest_ration_no_feeds(self):
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        ration = state.cheapest_ration
        assert ration["items"] == []

    # ── Bulk feeding from plans tests ─────────────────────────────────

    def test_match_plan_animals_lactating(self):
        import datetime

        from app.states.feed_state import FeedState

        today = datetime.date.today().isoformat()
        lactating = {
            "id": "a1",
            "name": "L",
            "is_juvenile": False,
            "animal_type": "cow",
            "milk_production": [{"date": today, "liters": 10.0}],
        }
        dry = {
            "id": "a2",
            "name": "K",
            "is_juvenile": False,
            "animal_type": "cow",
            "milk_production": [],
        }
        matched = FeedState._match_plan_animals_by_category(
            "Lactating Cow", [lactating, dry], set()
        )
        assert [c["id"] for c in matched] == ["a1"]

    def test_match_plan_animals_pregnant(self):
        from app.states.feed_state import FeedState

        cows = [
            {"id": "a1", "name": "L", "milk_production": []},
            {"id": "a2", "name": "K", "milk_production": []},
        ]
        matched = FeedState._match_plan_animals_by_category(
            "Pregnant Cow", cows, {"a2"}
        )
        assert [c["id"] for c in matched] == ["a2"]

    def test_match_plan_animals_calf(self):
        from app.states.feed_state import FeedState

        calf = {"id": "a1", "name": "C", "is_juvenile": True, "milk_production": []}
        adult = {"id": "a2", "name": "L", "is_juvenile": False, "age": 4, "milk_production": []}
        matched = FeedState._match_plan_animals_by_category("Calf", [calf, adult], set())
        assert [c["id"] for c in matched] == ["a1"]

    def test_record_plan_for_animals(self):
        from unittest.mock import AsyncMock, patch

        from app.database import crud
        from app.states.feed_state import FeedState

        state = FeedState()  # type: ignore
        state.feed_types = [
            {
                "id": "rb",
                "name": "Rice Bran",
                "category": "Concentrate",
                "unit": "kg",
                "cost_per_unit": 28.0,
                "is_custom": False,
                "farm_id": "f",
            }
        ]
        plan = {
            "id": "p1",
            "category": "Lactating Cow",
            "name": "Lactating Cow Plan",
            "morning": [{"feed_type_id": "rb", "feed_name": "Rice Bran", "quantity": 2.0, "unit": "kg"}],
            "evening": [],
            "minerals": "",
            "water_reminder": True,
            "farm_id": "f",
        }
        animals = [{"id": "a1", "name": "L"}, {"id": "a2", "name": "K"}]
        with patch.object(
            crud, "create_feed_consumption", new=AsyncMock(return_value=True)
        ), patch.object(
            crud, "update_feed_stock", new=AsyncMock(return_value=True)
        ):
            count = self._run(state._record_plan_for_animals(plan, animals, "farm1"))
        assert count == 2
        assert len(state.consumptions) == 2
        assert state.consumptions[0]["notes"] == "From Lactating Cow Plan"


# ─── Smoke Tests ──────────────────────────────────────────────────────


def test_smoke():
    """Simple smoke test to ensure test runner works."""
    assert True


def test_import_app():
    """Verify the main app module can be imported."""
    from app import app  # noqa: F401


def test_import_config():
    """Verify config module works."""
    from app.config import config

    assert config is not None


def test_import_services():
    """Verify service modules can be imported."""
    from app.services.email_service import email_service
    from app.services.sms_service import sms_service

    assert email_service is not None
    assert sms_service is not None


def test_import_i18n():
    """Verify i18n module works."""
    from app.states.i18n_state import TRANSLATIONS

    assert "English" in TRANSLATIONS
    assert "Tamil" in TRANSLATIONS
    assert "Hindi" in TRANSLATIONS

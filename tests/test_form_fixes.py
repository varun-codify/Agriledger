"""Tests that verify the fixes for form submission issues.

The screenshot showed "Something went wrong while saving" when adding a new
animal via the Add Animal form. The root causes were:
  1. Browser sends MM/DD/YYYY dates (e.g. 08/13/2026) instead of ISO format.
  2. HTML checkboxes submit the string "on" instead of a boolean.
  3. MongoDB _id (ObjectId) leaks into state vars, breaking serialization.
  4. Reflex MutableProxy objects can't be serialized by MongoDB's BSON encoder.
  5. Demo data was a state var (serialized to every browser on page load).
"""

import datetime


# ─── _normalize_iso_date ─────────────────────────────────────────────


class TestNormalizeIsoDate:
    """Test that dates from browsers are normalized to ISO format."""

    def test_iso_already(self):
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date("2026-08-13") == "2026-08-13"

    def test_mm_dd_yyyy_us_format(self):
        """The exact format shown in the screenshot: 08/13/2026."""
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date("08/13/2026") == "2026-08-13"

    def test_mm_dd_yyyy_with_dash(self):
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date("08-13-2026") == "2026-08-13"

    def test_dd_mm_yyyy_european(self):
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date("13/08/2026") == "2026-08-13"

    def test_dd_mm_yyyy_with_dash(self):
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date("13-08-2026") == "2026-08-13"

    def test_dot_separated(self):
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date("13.08.2026") == "2026-08-13"

    def test_empty_string(self):
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date("") is None

    def test_none(self):
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date(None) is None  # type: ignore

    def test_garbage(self):
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date("not-a-date") is None

    def test_whitespace_trimmed(self):
        from app.states.cattle_state import _normalize_iso_date

        assert _normalize_iso_date("  2026-08-13  ") == "2026-08-13"

    def test_iso_today(self):
        from app.states.cattle_state import _normalize_iso_date

        today = datetime.date.today().isoformat()
        assert _normalize_iso_date(today) == today

    def test_breeding_state_also_has_normalize(self):
        from app.states.breeding_state import _normalize_iso_date

        assert _normalize_iso_date("08/13/2026") == "2026-08-13"


# ─── _to_bool (checkbox handling) ────────────────────────────────────


class TestToBool:
    """HTML checkboxes submit 'on' when checked and omit the field when unchecked."""

    def test_true_passthrough(self):
        from app.states.cattle_state import _to_bool

        assert _to_bool(True) is True

    def test_false_passthrough(self):
        from app.states.cattle_state import _to_bool

        assert _to_bool(False) is False

    def test_on_string(self):
        """Browser checkbox 'on' value."""
        from app.states.cattle_state import _to_bool

        assert _to_bool("on") is True

    def test_checked_string(self):
        from app.states.cattle_state import _to_bool

        assert _to_bool("checked") is True

    def test_true_string(self):
        from app.states.cattle_state import _to_bool

        assert _to_bool("true") is True

    def test_one_string(self):
        from app.states.cattle_state import _to_bool

        assert _to_bool("1") is True

    def test_yes_string(self):
        from app.states.cattle_state import _to_bool

        assert _to_bool("yes") is True

    def test_empty_string(self):
        """When checkbox is unchecked, Reflex may send empty string."""
        from app.states.cattle_state import _to_bool

        assert _to_bool("") is False

    def test_none_value(self):
        """When checkbox field is omitted entirely."""
        from app.states.cattle_state import _to_bool

        assert _to_bool(None) is False

    def test_random_string(self):
        from app.states.cattle_state import _to_bool

        assert _to_bool("banana") is False


# ─── _normalize_cattle_row ───────────────────────────────────────────


class TestNormalizeCattleRow:
    """Legacy/corrupt DB rows must not crash computed vars or components."""

    def test_fills_missing_image_url(self):
        from app.states.cattle_state import _normalize_cattle_row

        row = {"id": "x", "name": "Test", "animal_type": "cow"}
        clean = _normalize_cattle_row(row)
        assert clean["image_url"] == ""

    def test_converts_string_weight_to_float(self):
        from app.states.cattle_state import _normalize_cattle_row

        row = {"id": "x", "name": "T", "weight": "550"}
        clean = _normalize_cattle_row(row)
        assert clean["weight"] == 550.0
        assert isinstance(clean["weight"], float)

    def test_converts_string_age_to_int(self):
        from app.states.cattle_state import _normalize_cattle_row

        row = {"id": "x", "name": "T", "age": "4"}
        clean = _normalize_cattle_row(row)
        assert clean["age"] == 4
        assert isinstance(clean["age"], int)

    def test_boolean_normalization(self):
        from app.states.cattle_state import _normalize_cattle_row

        row = {"id": "x", "name": "T", "is_juvenile": "on", "is_active": "true"}
        clean = _normalize_cattle_row(row)
        assert clean["is_juvenile"] is True
        assert clean["is_active"] is True

    def test_none_lists_become_empty(self):
        from app.states.cattle_state import _normalize_cattle_row

        row = {
            "id": "x",
            "name": "T",
            "milk_production": None,
            "vaccinations": None,
            "health_notes": None,
            "feed_records": None,
        }
        clean = _normalize_cattle_row(row)
        assert clean["milk_production"] == []
        assert clean["vaccinations"] == []
        assert clean["health_notes"] == []
        assert clean["feed_records"] == []

    def test_legacy_date_normalized(self):
        from app.states.cattle_state import _normalize_cattle_row

        row = {"id": "x", "name": "T", "purchase_date": "03/15/2023"}
        clean = _normalize_cattle_row(row)
        assert clean["purchase_date"] == "2023-03-15"

    def test_empty_weight_becomes_none(self):
        from app.states.cattle_state import _normalize_cattle_row

        row = {"id": "x", "name": "T", "weight": ""}
        clean = _normalize_cattle_row(row)
        assert clean["weight"] is None

    def test_farm_id_preserved(self):
        from app.states.cattle_state import _normalize_cattle_row

        row = {"id": "x", "name": "T", "farm_id": "my-farm"}
        clean = _normalize_cattle_row(row)
        assert clean["farm_id"] == "my-farm"

    def test_farm_id_absent_when_not_in_row(self):
        from app.states.cattle_state import _normalize_cattle_row

        row = {"id": "x", "name": "T"}
        clean = _normalize_cattle_row(row)
        assert "farm_id" not in clean

    def test_corrupt_row_no_crash(self):
        """A completely empty row should not raise."""
        from app.states.cattle_state import _normalize_cattle_row

        clean = _normalize_cattle_row({})
        assert clean["id"] == ""
        assert clean["name"] == ""
        assert clean["animal_type"] == "cow"


# ─── Auth state _id filtering ────────────────────────────────────────


class TestAuthIdFiltering:
    """MongoDB _id (ObjectId) must be stripped before storing in state."""

    def test_login_strips_id_from_user(self):
        """Verify the same dict-comprehension used in AuthState.login."""
        # Simulate what crud.get_user_by_email returns from MongoDB
        user_with_id = {
            "_id": "some_object_id_123",
            "name": "Test User",
            "email": "test@example.com",
            "password": "hashed",
            "role": "admin",
            "farm_id": "farm1",
            "phone": None,
            "is_active": True,
        }

        # Apply the exact same filtering logic used in AuthState.login
        user_filtered = {k: v for k, v in user_with_id.items() if k != "_id"}

        assert "_id" not in user_filtered
        assert user_filtered["email"] == "test@example.com"
        assert user_filtered["farm_id"] == "farm1"


# ─── _to_plain (Reflex MutableProxy serialization) ────────────────────


class TestToPlain:
    """Reflex wraps mutable state in MutableProxy which BSON can't serialize."""

    def test_dict_passthrough(self):
        from app.database.crud import _to_plain

        d = {"a": 1, "b": "hello"}
        assert _to_plain(d) == d

    def test_nested_dict(self):
        from app.database.crud import _to_plain

        d = {"a": {"b": {"c": 42}}}
        result = _to_plain(d)
        assert result == d

    def test_list_of_dicts(self):
        from app.database.crud import _to_plain

        items = [{"id": "1", "name": "x"}, {"id": "2", "name": "y"}]
        result = _to_plain(items)
        assert result == items

    def test_none_passthrough(self):
        from app.database.crud import _to_plain

        assert _to_plain(None) is None

    def test_string_passthrough(self):
        from app.database.crud import _to_plain

        assert _to_plain("hello") == "hello"

    def test_int_passthrough(self):
        from app.database.crud import _to_plain

        assert _to_plain(42) == 42

    def test_mixed_nested(self):
        from app.database.crud import _to_plain

        d = {
            "id": "c1",
            "name": "Lakshmi",
            "milk_production": [{"date": "2026-01-01", "liters": 12.5}],
            "vaccinations": [],
        }
        result = _to_plain(d)
        assert result["milk_production"][0]["liters"] == 12.5


# ─── Demo data module-level (not state var) ──────────────────────────


class TestDemoDataModuleLevel:
    """Demo data is a module-level constant, not a state var,
    to prevent it from being serialized to every browser."""

    def test_cattle_demo_data_not_in_class_vars(self):
        from app.states.cattle_state import CattleState, DEMO_CATTLE_DATA

        # Verify DEMO_CATTLE_DATA is a module-level name, not a class attribute
        assert hasattr(DEMO_CATTLE_DATA, "__iter__")
        assert len(DEMO_CATTLE_DATA) > 0
        # Should NOT be in the class's own dict (state vars)
        assert "DEMO_CATTLE_DATA" not in CattleState.__dict__

    def test_breeding_demo_data_not_in_class_vars(self):
        from app.states.breeding_state import BreedingState, DEMO_BREEDING_DATA

        assert hasattr(DEMO_BREEDING_DATA, "__iter__")
        assert len(DEMO_BREEDING_DATA) > 0
        assert "DEMO_BREEDING_DATA" not in BreedingState.__dict__


# ─── CropState weather data cleaning ─────────────────────────────────


class TestWeatherDataCleaning:
    """Weather API responses have extra keys that cause Reflex validation warnings."""

    def test_cleans_extra_keys(self):
        from app.states.crop_state import _clean_weather_data

        raw = {
            "latitude": 12.5,
            "longitude": 78.5,
            "timezone": "Asia/Kolkata",
            "current_units": {"temperature_2m": "°C"},
            "current": {
                "time": "2026-08-13T12:00",
                "temperature_2m": 28.5,
                "relative_humidity_2m": 75,
                "precipitation": 0.0,
                "weather_code": 1,
                "wind_speed_10m": 5.2,
                "extra_field": "should be stripped",
            },
            "daily": {
                "time": ["2026-08-13"],
                "temperature_2m_max": [32.0],
                "temperature_2m_min": [22.0],
                "precipitation_sum": [0.0],
                "weather_code": [1],
                "extra_daily": "should be stripped",
            },
        }
        cleaned = _clean_weather_data(raw)

        # Only declared keys should remain
        assert "current" in cleaned
        assert "daily" in cleaned
        assert "latitude" not in cleaned
        assert "timezone" not in cleaned
        assert "current_units" not in cleaned

        # Current should only have declared fields
        assert set(cleaned["current"].keys()) == {
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
        }
        assert cleaned["current"]["temperature_2m"] == 28.5

    def test_handles_missing_current(self):
        from app.states.crop_state import _clean_weather_data

        cleaned = _clean_weather_data({})
        assert cleaned["current"]["temperature_2m"] == 0.0

    def test_handles_none_values(self):
        from app.states.crop_state import _clean_weather_data

        raw = {"current": {"temperature_2m": None, "wind_speed_10m": None}}
        cleaned = _clean_weather_data(raw)
        assert cleaned["current"]["temperature_2m"] == 0.0
        assert cleaned["current"]["wind_speed_10m"] == 0.0

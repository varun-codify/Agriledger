"""Tests for the Milk & Society Bills feature.

Covers: model fields, fat%-slab rate suggestion, defensive field setters,
bill-amount mismatch detection, and OCR result application.
"""

import datetime
from typing import get_type_hints


class TestMilkSaleModel:
    """Milk sale records must carry the society-bill fields."""

    def test_milk_sale_has_bill_fields(self):
        from app.database.models import MilkSale

        hints = get_type_hints(MilkSale)
        for field in ("bill_number", "payment_status", "paid_date", "clr"):
            assert field in hints

    def test_rate_table_model_exists(self):
        from app.database.models import MilkSocietyRate, MilkSocietyRateSlab

        assert "slabs" in MilkSocietyRate.__annotations__
        assert "fat_min" in MilkSocietyRateSlab.__annotations__


class TestRateSuggestion:
    """The rate checker picks the highest fat%-slab at or below the reading."""

    def test_returns_highest_matching_slab(self):
        from app.states.milk_state import _suggest_rate_for_fat

        slabs = [
            {"fat_min": 3.0, "rate": 40.0},
            {"fat_min": 4.0, "rate": 44.0},
            {"fat_min": 5.0, "rate": 50.0},
        ]
        assert _suggest_rate_for_fat(3.0, slabs) == 40.0
        assert _suggest_rate_for_fat(4.5, slabs) == 44.0
        assert _suggest_rate_for_fat(5.2, slabs) == 50.0
        assert _suggest_rate_for_fat(2.9, slabs) == 0.0

    def test_ignores_invalid_slabs(self):
        from app.states.milk_state import _suggest_rate_for_fat

        slabs = [{"fat_min": 3.0, "rate": 40.0}, {"fat_min": "bad", "rate": 999}]
        assert _suggest_rate_for_fat(4.0, slabs) == 40.0


class TestMilkStateFields:
    """Setters must be defensive: clamp ranges, never crash on garbage."""

    def test_setters_clamp_values(self):
        from app.states.milk_state import MilkState

        state = MilkState()  # type: ignore
        state.set_fat_percentage("12")
        assert state.fat_percentage == 10.0
        state.set_snf_percentage("4")
        assert state.snf_percentage == 6.0
        state.set_liters("50")
        assert state.liters == 50.0

    def test_setters_tolerate_garbage(self):
        from app.states.milk_state import MilkState

        state = MilkState()  # type: ignore
        state.set_liters("abc")
        assert state.liters == 0.0
        state.set_rate_per_liter(None)
        assert state.rate_per_liter == 0.0

    def test_payment_status_whitelist(self):
        from app.states.milk_state import MilkState

        state = MilkState()  # type: ignore
        state.set_payment_status("paid")
        assert state.payment_status == "paid"
        state.set_payment_status("evil")
        assert state.payment_status == "pending"

    def test_mismatch_detection(self):
        """Bill amount that disagrees with litres x rate must be flagged."""
        from app.states.milk_state import MilkState

        state = MilkState()  # type: ignore
        state.liters = 12.5
        state.rate_per_liter = 40.0
        state.amount = 500.0
        assert state.expected_amount == 500.0
        assert not state.amount_mismatch
        state.amount = 600.0
        assert state.amount_mismatch


class TestOcrApplication:
    """OCR output must be sanitized before filling the form."""

    def test_ocr_fills_form(self):
        from app.states.milk_state import MilkState

        state = MilkState()  # type: ignore
        state._apply_ocr_result(
            {
                "date": "2026-08-01",
                "society": "Aavin",
                "litres": "12.5",
                "fat_percentage": "4.2",
                "snf_percentage": "8.5",
                "total_amount": 500,
                "bill_number": "B-1024",
            }
        )
        assert state.liters == 12.5
        assert state.fat_percentage == 4.2
        assert state.snf_percentage == 8.5
        assert state.amount == 500.0
        assert state.bill_number == "B-1024"

    def test_ocr_rejects_future_dates(self):
        from app.states.milk_state import MilkState

        state = MilkState()  # type: ignore
        future = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        state._apply_ocr_result({"date": future})
        assert state.date == datetime.date.today().isoformat()

    def test_ocr_clamps_out_of_range_values(self):
        from app.states.milk_state import MilkState

        state = MilkState()  # type: ignore
        state._apply_ocr_result(
            {"fat_percentage": 99, "snf_percentage": 1, "litres": -5}
        )
        assert state.fat_percentage == 10.0
        assert state.snf_percentage == 6.0
        assert state.liters == 0.0

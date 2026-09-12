"""Tests for AgriLedger production readiness improvements."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.api import app
from app.database import crud
from app.database.connection import ping_db
from app.middleware.rate_limiter import RateLimitMiddleware
from app.states.settings_state import SettingsState


def _run(coro):
    return asyncio.run(coro)


# --- Multi-Tenant CRUD Scoping Tests -----------------------------------

def test_update_cattle_multi_tenant_scoping():
    mock_db = MagicMock()
    mock_db.cattle.update_one = AsyncMock(return_value=MagicMock(matched_count=1, modified_count=1))
    
    with patch("app.database.crud.get_db", return_value=mock_db):
        res = _run(crud.update_cattle("c123", {"name": "Daisy 2"}, farm_id="farm-456"))
        assert res is True
        mock_db.cattle.update_one.assert_called_once_with(
            {"id": "c123", "farm_id": "farm-456"},
            {"$set": {"name": "Daisy 2"}}
        )


def test_update_crop_multi_tenant_scoping():
    mock_db = MagicMock()
    mock_db.crops.update_one = AsyncMock(return_value=MagicMock(matched_count=1, modified_count=1))
    
    with patch("app.database.crud.get_db", return_value=mock_db):
        res = _run(crud.update_crop("crop-1", {"status": "Harvested"}, farm_id="farm-456"))
        assert res is True
        mock_db.crops.update_one.assert_called_once_with(
            {"id": "crop-1", "farm_id": "farm-456"},
            {"$set": {"status": "Harvested"}}
        )


def test_update_milk_sale_multi_tenant_scoping():
    mock_db = MagicMock()
    mock_db.milk_sales.update_one = AsyncMock(return_value=MagicMock(matched_count=1, modified_count=1))
    
    with patch("app.database.crud.get_db", return_value=mock_db):
        res = _run(crud.update_milk_sale("sale-1", {"payment_status": "paid"}, farm_id="farm-456"))
        assert res is True
        mock_db.milk_sales.update_one.assert_called_once_with(
            {"id": "sale-1", "farm_id": "farm-456"},
            {"$set": {"payment_status": "paid"}}
        )


def test_delete_milk_sale_multi_tenant_scoping():
    mock_db = MagicMock()
    mock_db.milk_sales.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    
    with patch("app.database.crud.get_db", return_value=mock_db):
        res = _run(crud.delete_milk_sale("sale-1", farm_id="farm-456"))
        assert res is True
        mock_db.milk_sales.delete_one.assert_called_once_with(
            {"id": "sale-1", "farm_id": "farm-456"}
        )


def test_update_user_profile():
    mock_db = MagicMock()
    mock_db.users.update_one = AsyncMock(return_value=MagicMock(matched_count=1, modified_count=1))
    
    with patch("app.database.crud.get_db", return_value=mock_db):
        res = _run(crud.update_user_profile("user@example.com", name="Jane Farmer", phone="1234567890"))
        assert res is True
        mock_db.users.update_one.assert_called_once_with(
            {"email": "user@example.com"},
            {"$set": {"name": "Jane Farmer", "phone": "1234567890"}}
        )


# --- Connection & Ping Tests -------------------------------------------

def test_ping_db_success():
    mock_db = MagicMock()
    mock_db.command = AsyncMock(return_value={"ok": 1})
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    with patch("app.database.connection.get_db_client", return_value=mock_client):
        assert _run(ping_db()) is True
        mock_db.command.assert_called_once_with("ping")


def test_ping_db_failure():
    with patch("app.database.connection.get_db_client", return_value=None):
        assert _run(ping_db()) is False


# --- Rate Limiter & Security Headers Middleware Tests ------------------

def test_rate_limiter_stale_cleanup():
    mw = RateLimitMiddleware(app=None, max_requests=10, window_seconds=60)
    mw.requests["1.1.1.1"] = [900.0, 920.0]  # Old timestamps (< 940)
    mw.requests["2.2.2.2"] = [980.0, 990.0]  # Fresh timestamp
    
    mw._cleanup_stale_entries(cutoff=940.0)
    assert "1.1.1.1" not in mw.requests
    assert "2.2.2.2" in mw.requests


# --- FastAPI Health & Security Headers Endpoints Tests -----------------

def test_health_endpoints():
    client = TestClient(app)
    with patch("app.api.ping_db", new=AsyncMock(return_value=True)):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "version" in data
        assert "environment" in data
        
        # Test security headers
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "SAMEORIGIN"


def test_api_health_endpoint():
    client = TestClient(app)
    with patch("app.api.ping_db", new=AsyncMock(return_value=False)):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["database"] == "disconnected"


# --- Settings Profile Persistence Test ---------------------------------

def test_settings_update_profile_saves_to_db():
    state = SettingsState()
    auth_mock = MagicMock()
    auth_mock.current_user = {"email": "farmer@example.com", "name": "Old Name"}
    
    with patch.object(SettingsState, "get_state", new=AsyncMock(return_value=auth_mock)), patch.object(
        crud, "update_user_profile", new=AsyncMock(return_value=True)
    ) as update_mock:
        _run(state.update_profile({"name": "New Farmer Name"}))
        update_mock.assert_awaited_once_with("farmer@example.com", name="New Farmer Name")
        auth_mock.update_current_user_name.assert_called_once_with("New Farmer Name")

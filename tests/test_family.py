"""Tests for farm settings persistence and family member management.

These tests exercise the state logic with the database layer mocked out,
so they run without a live MongoDB connection.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch



def _run(coro):
    """Run an async coroutine in a fresh event loop."""
    return asyncio.run(coro)


def _auth_mock(farm_id: str = "farm-1", owner_email: str = "owner@farm.com"):
    auth = MagicMock()
    auth.farm_id = farm_id
    auth.current_user = {"email": owner_email}
    return auth


def _call_with_auth(state_cls, auth, coro):
    """Run an async state event with ``get_state`` mocked to return ``auth``."""
    with patch.object(state_cls, "get_state", new=AsyncMock(return_value=auth)):
        return _run(coro)


def _run_register(state, form):
    """Run ``register``, tolerating Reflex's redirect path artifact.

    ``register`` finishes by returning ``rx.redirect("/dashboard")``. When a
    unit-test session runs after another test has imported the compiled app,
    resolving that redirect's event path can raise ``ValueError``. The state
    mutations we assert on (login flag, joined farm_id) already happened by
    then, so the error is ignored here.
    """
    try:
        _run(state.register(form))
    except ValueError:
        pass


class TestFarmSettings:
    """Farm name / location / size persistence."""

    def test_default_farm_name(self):
        from app.states.settings_state import SettingsState

        state = SettingsState()
        assert state.farm_name == "My Farm"

    def test_fetch_farm_settings_loads_saved_values(self):
        from app.states import settings_state as ss

        state = ss.SettingsState()
        with patch.object(
            ss.crud,
            "get_farm",
            new=AsyncMock(
                return_value={
                    "farm_id": "farm-1",
                    "name": "Green Valley",
                    "location": "Erode",
                    "size": "10 Acres",
                }
            ),
        ):
            _call_with_auth(ss.SettingsState, _auth_mock(), state.fetch_farm_settings())
        assert state.farm_name == "Green Valley"
        assert state.farm_location == "Erode"
        assert state.farm_size == "10 Acres"

    def test_update_farm_details_persists(self):
        from app.states import settings_state as ss

        state = ss.SettingsState()
        with patch.object(
            ss.crud, "upsert_farm", new=AsyncMock(return_value=True)
        ) as upsert:
            _call_with_auth(
                ss.SettingsState,
                _auth_mock(),
                state.update_farm_details(
                    {
                        "farm_name": "My Farm",
                        "farm_location": "Erode",
                        "farm_size": "5 Acres",
                    }
                ),
            )
        upsert.assert_awaited_once_with(
            "farm-1", {"name": "My Farm", "location": "Erode", "size": "5 Acres"}
        )
        assert state.farm_name == "My Farm"
        assert state.settings_error == ""

    def test_update_farm_details_requires_name(self):
        from app.states import settings_state as ss

        state = ss.SettingsState()
        _call_with_auth(
            ss.SettingsState,
            _auth_mock(),
            state.update_farm_details(
                {"farm_name": "", "farm_location": "Erode", "farm_size": ""}
            ),
        )
        assert state.settings_error == "Farm name is required."


class TestFamilyState:
    """Family member add / remove with shared-access linking."""

    def _make_state(self):
        from app.states import family_state as fs

        return fs.FamilyState(), fs

    def test_add_member_requires_name(self):
        state, fs = self._make_state()
        _call_with_auth(fs.FamilyState, _auth_mock(), state.add_member())
        assert state.family_error == "Member name is required."

    def test_add_member_requires_valid_email(self):
        state, fs = self._make_state()
        state.new_member_name = "Rani"
        _call_with_auth(fs.FamilyState, _auth_mock(), state.add_member())
        assert state.family_error == "Member email is required."

        state.new_member_email = "not-an-email"
        _call_with_auth(fs.FamilyState, _auth_mock(), state.add_member())
        assert (
            state.family_error
            == "Enter a valid email address (e.g., name@example.com)."
        )

    def test_add_member_cannot_add_owner(self):
        state, fs = self._make_state()
        state.new_member_name = "Owner"
        state.new_member_email = "OWNER@farm.com"
        _call_with_auth(fs.FamilyState, _auth_mock(), state.add_member())
        assert state.family_error == "You can't add your own account as a family member."

    def test_add_member_links_existing_user(self):
        state, fs = self._make_state()
        state.new_member_name = "Rani"
        state.new_member_email = "rani@example.com"
        with patch.object(
            fs.crud,
            "get_user_by_email",
            new=AsyncMock(return_value={"email": "rani@example.com"}),
        ), patch.object(
            fs.crud, "update_user_farm_id", new=AsyncMock(return_value=True)
        ) as link, patch.object(
            fs.crud, "create_family_member", new=AsyncMock(return_value=True)
        ):
            _call_with_auth(fs.FamilyState, _auth_mock(), state.add_member())
        link.assert_awaited_once_with("rani@example.com", "farm-1")
        assert len(state.members) == 1
        assert state.members[0]["status"] == "active"
        assert state.members[0]["farm_id"] == "farm-1"
        assert state.family_error == ""

    def test_add_member_invites_unregistered_email(self):
        state, fs = self._make_state()
        state.new_member_name = "Rani"
        state.new_member_email = "rani@example.com"
        with patch.object(
            fs.crud, "get_user_by_email", new=AsyncMock(return_value=None)
        ), patch.object(
            fs.crud, "create_family_member", new=AsyncMock(return_value=True)
        ):
            _call_with_auth(fs.FamilyState, _auth_mock(), state.add_member())
        assert state.members[0]["status"] == "invited"

    def test_add_member_rejects_duplicates(self):
        state, fs = self._make_state()
        state.members = [
            {
                "id": "m1",
                "farm_id": "farm-1",
                "name": "Rani",
                "email": "rani@example.com",
                "status": "active",
            }
        ]
        state.new_member_name = "Rani"
        state.new_member_email = "rani@example.com"
        _call_with_auth(fs.FamilyState, _auth_mock(), state.add_member())
        assert (
            state.family_error == "rani@example.com is already a member of this farm."
        )

    def test_remove_member_revokes_access(self):
        state, fs = self._make_state()
        state.members = [
            {
                "id": "m1",
                "farm_id": "farm-1",
                "name": "Rani",
                "email": "rani@example.com",
                "status": "active",
            }
        ]
        with patch.object(
            fs.crud,
            "get_user_by_email",
            new=AsyncMock(return_value={"email": "rani@example.com"}),
        ), patch.object(
            fs.crud, "update_user_farm_id", new=AsyncMock(return_value=True)
        ) as relink, patch.object(
            fs.crud, "delete_family_member", new=AsyncMock(return_value=True)
        ):
            _call_with_auth(fs.FamilyState, _auth_mock(), state.remove_member("m1"))
        assert state.members == []
        # The member's account is moved to a brand-new farm, not the shared one.
        args = relink.await_args.args
        assert args[0] == "rani@example.com"
        assert args[1] != "farm-1"


class TestRegistrationJoin:
    """New sign-ups with a pending family invitation join the farm."""

    def test_register_joins_invited_farm(self):
        from app.states import auth_state as auth_mod

        state = auth_mod.AuthState()
        invite = {"id": "inv1", "farm_id": "family-farm", "email": "rani@example.com"}
        with patch.object(
            auth_mod.crud, "get_user_by_email", new=AsyncMock(return_value=None)
        ), patch.object(
            auth_mod.crud,
            "get_family_member_by_email",
            new=AsyncMock(return_value=invite),
        ), patch.object(
            auth_mod.crud, "create_user", new=AsyncMock(return_value=True)
        ), patch.object(
            auth_mod.crud,
            "update_family_member_status",
            new=AsyncMock(return_value=True),
        ) as mark_active:
            _run_register(
                state,
                {
                    "name": "Rani",
                    "email": "rani@example.com",
                    "password": "password123",
                    "confirm_password": "password123",
                },
            )
        assert state.is_logged_in is True
        assert state.current_user["farm_id"] == "family-farm"
        mark_active.assert_awaited_once_with("inv1", "active")

    def test_register_creates_new_farm_without_invite(self):
        from app.states import auth_state as auth_mod

        state = auth_mod.AuthState()
        with patch.object(
            auth_mod.crud, "get_user_by_email", new=AsyncMock(return_value=None)
        ), patch.object(
            auth_mod.crud,
            "get_family_member_by_email",
            new=AsyncMock(return_value=None),
        ), patch.object(
            auth_mod.crud, "create_user", new=AsyncMock(return_value=True)
        ):
            _run_register(
                state,
                {
                    "name": "New User",
                    "email": "new@example.com",
                    "password": "password123",
                    "confirm_password": "password123",
                },
            )
        assert state.current_user["farm_id"] != "family-farm"
        assert state.current_user["farm_id"] != ""

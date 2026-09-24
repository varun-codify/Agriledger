"""Family members who share access to a farm.

The farm owner adds members by email from Settings. If the member already has
an account, their ``farm_id`` is pointed at this farm so they see the same
data after they log in. If they don't have an account yet, they are stored as
an ``invited`` member and automatically join this farm when they sign up.
Removing a member revokes access by re-pointing their account at a fresh farm.
"""

import datetime
import re
import uuid

import reflex as rx

from app.database import crud
from app.database.models import FamilyMember
from app.states.auth_state import AuthState

_EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")


class FamilyState(rx.State):
    """Manages the family members who share access to this farm."""

    members: list[FamilyMember] = []
    new_member_name: str = ""
    new_member_email: str = ""
    new_member_phone: str = ""
    family_error: str = ""
    pending_delete_id: str = ""

    # ── Form field setters ─────────────────────────────────────────────

    @rx.event
    def set_new_member_name(self, value: str):
        self.new_member_name = value

    @rx.event
    def set_new_member_email(self, value: str):
        self.new_member_email = value

    @rx.event
    def set_new_member_phone(self, value: str):
        self.new_member_phone = value

    @rx.event
    def set_pending_delete_id(self, value: str):
        self.pending_delete_id = value

    # ── Data loading ───────────────────────────────────────────────────

    @rx.event
    async def fetch_members(self):
        """Load the family members for the current farm."""
        auth = await self.get_state(AuthState)
        self.members = await crud.get_family_members(auth.farm_id)

    # ── Adding / removing members ──────────────────────────────────────

    @rx.event
    async def add_member(self):
        """Add a family member: link existing accounts, invite the rest."""
        self.family_error = ""
        name = self.new_member_name.strip()
        email = self.new_member_email.strip()
        phone = self.new_member_phone.strip() or None
        if not name:
            self.family_error = "Member name is required."
            return
        if not email:
            self.family_error = "Member email is required."
            return
        if not _EMAIL_RE.fullmatch(email):
            self.family_error = "Enter a valid email address (e.g., name@example.com)."
            return

        auth = await self.get_state(AuthState)
        owner_email = (auth.current_user or {}).get("email")
        if owner_email and email.lower() == owner_email.lower():
            self.family_error = "You can't add your own account as a family member."
            return
        if any(m["email"].lower() == email.lower() for m in self.members):
            self.family_error = f"{email} is already a member of this farm."
            return

        member: FamilyMember = {
            "id": str(uuid.uuid4()),
            "farm_id": auth.farm_id,
            "name": name,
            "email": email,
            "phone": phone,
            "role": "member",
            "status": "active",
            "added_date": datetime.date.today().isoformat(),
        }
        try:
            linked_user = await crud.get_user_by_email(email)
        except Exception:
            linked_user = None
        if linked_user:
            # Already registered: point their account at this farm so they
            # see the same data after their next login.
            await crud.update_user_farm_id(email, auth.farm_id)
        else:
            # Not registered yet: they join automatically at sign-up.
            member["status"] = "invited"
        if not await crud.create_family_member(member):
            self.family_error = "Could not save the member. Please try again."
            return

        self.members.append(member)
        self.new_member_name = ""
        self.new_member_email = ""
        self.new_member_phone = ""
        if member["status"] == "invited":
            return rx.toast.success(
                f"Invitation saved — {email} will join this farm when they sign up."
            )
        return rx.toast.success(f"{name} now shares access to this farm.")

    @rx.event
    async def remove_member(self, member_id: str):
        """Remove a member and revoke their access to this farm."""
        auth = await self.get_state(AuthState)
        member = next((m for m in self.members if m["id"] == member_id), None)
        if not member:
            self.pending_delete_id = ""
            return
        # If the member has an account, move it to a fresh farm so they can
        # no longer see this farm's data (their old records stay here).
        try:
            linked_user = await crud.get_user_by_email(member["email"])
        except Exception:
            linked_user = None
        if linked_user:
            await crud.update_user_farm_id(member["email"], str(uuid.uuid4()))
        await crud.delete_family_member(auth.farm_id, member_id)
        self.members = [m for m in self.members if m["id"] != member_id]
        self.pending_delete_id = ""
        return rx.toast.success(f"{member['name']} was removed from the farm.")

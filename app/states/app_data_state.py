"""Consolidated page data loading.

Every protected page used to fire 4–8 separate ``on_load`` events (cattle,
crops, transactions, breeding, feed, settings, weather, sync…). Each event is
its own websocket round-trip that re-reads the shared auth state, so pages
loaded as a slow sequential waterfall.

These loaders hydrate the session once, fetch everything a page needs **in
parallel** with ``asyncio.gather`` (each handler only touches its own state),
and then run the crop→feed auto-sync once at the end. Pages now make one
websocket call instead of up to eight.
"""

import asyncio
import logging

import reflex as rx

from app.states.auth_state import AuthState
from app.states.breeding_state import BreedingState
from app.states.cattle_state import CattleState
from app.states.crop_state import CropState
from app.states.family_state import FamilyState
from app.states.feed_state import FeedState
from app.states.settings_state import SettingsState
from app.states.transaction_state import TransactionState

logger = logging.getLogger(__name__)


class AppDataState(rx.State):
    """Loads all page data in parallel behind a single event."""

    # True while a page's data load is in flight — drives skeleton loaders.
    # Starts True so the first dashboard paint shows skeletons, not empty cards.
    is_loading: bool = True

    async def _gather_or_log(self, coros: list, label: str) -> None:
        """Run fetch coroutines concurrently; failures are logged, never fatal."""
        results = await asyncio.gather(*coros, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logger.exception(
                    "Page data load (%s) partially failed: %s", label, result
                )

    async def _load_core(self, include_weather: bool = False) -> None:
        """Shared loader: hydrate session, then fetch in parallel."""
        self.is_loading = True
        try:
            auth = await self.get_state(AuthState)
            if not auth.is_logged_in:
                return rx.redirect("/login")
            await auth.hydrate_user()
            if not auth.farm_id:
                return None

            cattle_state = await self.get_state(CattleState)
            tx_state = await self.get_state(TransactionState)
            crop_state = await self.get_state(CropState)
            breeding_state = await self.get_state(BreedingState)
            feed_state = await self.get_state(FeedState)
            settings_state = await self.get_state(SettingsState)

            coros = [
                cattle_state.fetch_cattle_list(),
                tx_state.fetch_transactions(),
                crop_state.fetch_crops_list(),
                breeding_state.fetch_breeding_cycles(),
                feed_state.fetch_feed_data(),
                settings_state.fetch_farm_settings(),
            ]
            if include_weather:
                coros.append(crop_state.fetch_weather())
            await self._gather_or_log(coros, "core")

            # Auto-sync depends on crops + feed being loaded; runs once at the end.
            try:
                await feed_state.auto_sync_homegrown_crops()
            except Exception as e:  # noqa: BLE001 - a failed sync must not break the page
                logger.warning("Crop-to-feed auto-sync failed: %s", e)
            return None
        finally:
            self.is_loading = False

    @rx.event
    async def load_dashboard_data(self):
        """Dashboard: everything, plus live weather."""
        return await self._load_core(include_weather=True)

    @rx.event
    async def load_page_data(self):
        """Standard protected page: all farm data in parallel."""
        return await self._load_core()

    @rx.event
    async def load_insights_data(self):
        """Insights hub: cattle, crops, transactions and weather (no breeding/feed)."""
        auth = await self.get_state(AuthState)
        if not auth.is_logged_in:
            return rx.redirect("/login")
        await auth.hydrate_user()
        if not auth.farm_id:
            return None

        cattle_state = await self.get_state(CattleState)
        tx_state = await self.get_state(TransactionState)
        crop_state = await self.get_state(CropState)
        await self._gather_or_log(
            [
                cattle_state.fetch_cattle_list(),
                tx_state.fetch_transactions(),
                crop_state.fetch_crops_list(),
                crop_state.fetch_weather(),
            ],
            "insights",
        )
        return None

    @rx.event
    async def load_settings_data(self):
        """Settings page: profile/farm settings + family members only."""
        auth = await self.get_state(AuthState)
        if not auth.is_logged_in:
            return rx.redirect("/login")
        await auth.hydrate_user()
        if not auth.farm_id:
            return None

        settings_state = await self.get_state(SettingsState)
        family_state = await self.get_state(FamilyState)
        await self._gather_or_log(
            [
                settings_state.fetch_farm_settings(),
                family_state.fetch_members(),
            ],
            "settings",
        )
        return None

    @rx.event
    async def load_reports_data(self):
        """Reports page: transactions only (previously could render zeros)."""
        auth = await self.get_state(AuthState)
        if not auth.is_logged_in:
            return rx.redirect("/login")
        await auth.hydrate_user()
        tx_state = await self.get_state(TransactionState)
        await tx_state.fetch_transactions()
        return None

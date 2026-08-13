"""PWA and scheduled automation utilities for AgriLedger.

Provides scheduled reminder checks, auto-email sending, and SMS alerts
for breeding cycles, vaccinations, weather, and payments.
"""

import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SchedulerService:
    """Provides methods to check and trigger scheduled reminders.

    In production, this would be run by a cron job or background task.
    """

    @staticmethod
    async def check_breeding_reminders(
        breeding_cycles: list[dict],
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> list[dict]:
        """Check for breeding-related reminders that need to be sent."""
        alerts = []
        today = datetime.date.today()
        next_7_days = today + datetime.timedelta(days=7)

        for cycle in breeding_cycles:
            insemination_date = datetime.date.fromisoformat(cycle["insemination_date"])

            # Pregnancy check due (30 days post-insemination)
            check_due = insemination_date + datetime.timedelta(days=30)
            if today >= check_due and not cycle.get("pregnancy_confirmed"):
                days_overdue = (today - check_due).days
                alerts.append({
                    "type": "breeding_check",
                    "animal": cycle["cattle_name"],
                    "message": f"Pregnancy check overdue by {days_overdue} days for {cycle['cattle_name']}",
                    "severity": "high",
                    "due_date": check_due.isoformat(),
                })

            # Calving expected soon
            calving_date = datetime.date.fromisoformat(cycle["expected_calving_date"])
            if today <= calving_date <= next_7_days and cycle.get("pregnancy_confirmed"):
                days_until = (calving_date - today).days
                alerts.append({
                    "type": "calving_expected",
                    "animal": cycle["cattle_name"],
                    "message": f"{cycle['cattle_name']} expected to calve in {days_until} day(s) ({calving_date})",
                    "severity": "medium",
                    "due_date": calving_date.isoformat(),
                })

            # Re-breeding indicator (cycle is > 30 days old with no pregnancy confirmed)
            if not cycle.get("pregnancy_confirmed") and cycle["status"] == "pending_confirmation":
                days_since = (today - insemination_date).days
                if days_since > 45:
                    alerts.append({
                        "type": "rebreeding",
                        "animal": cycle["cattle_name"],
                        "message": f"{cycle['cattle_name']} has not been confirmed pregnant after {days_since} days. Consider re-breeding.",
                        "severity": "medium",
                        "due_date": today.isoformat(),
                    })

        return alerts

    @staticmethod
    async def check_vaccination_reminders(
        cattle_list: list[dict],
    ) -> list[dict]:
        """Check for upcoming or overdue vaccination dates."""
        alerts = []
        today = datetime.date.today()
        next_14_days = today + datetime.timedelta(days=14)

        for animal in cattle_list:
            for vaccination in animal.get("vaccinations", []):
                next_due = vaccination.get("next_due_date")
                if not next_due:
                    continue
                due_date = datetime.date.fromisoformat(next_due)
                if today <= due_date <= next_14_days:
                    days_until = (due_date - today).days
                    alerts.append({
                        "type": "vaccination",
                        "animal": animal["name"],
                        "message": f"{vaccination['vaccine_name']} due for {animal['name']} in {days_until} day(s)",
                        "severity": "medium" if days_until > 3 else "high",
                        "due_date": next_due,
                    })
                elif today > due_date:
                    days_overdue = (today - due_date).days
                    alerts.append({
                        "type": "vaccination_overdue",
                        "animal": animal["name"],
                        "message": f"{vaccination['vaccine_name']} OVERDUE by {days_overdue} days for {animal['name']}",
                        "severity": "high",
                        "due_date": next_due,
                    })

        return alerts

    @staticmethod
    async def check_health_reminders(
        cattle_list: list[dict],
    ) -> list[dict]:
        """Check for animals needing attention."""
        alerts = []
        for animal in cattle_list:
            if animal.get("health_status") in ["Sick", "Under Treatment"]:
                alerts.append({
                    "type": "health",
                    "animal": animal["name"],
                    "message": f"{animal['name']} is {animal['health_status']}. Needs attention.",
                    "severity": "high",
                })
        return alerts

    @staticmethod
    async def generate_all_alerts(
        breeding_cycles: list[dict],
        cattle_list: list[dict],
    ) -> list[dict]:
        """Generate all alerts from all sources."""
        all_alerts = []
        all_alerts.extend(
            await SchedulerService.check_breeding_reminders(breeding_cycles)
        )
        all_alerts.extend(
            await SchedulerService.check_vaccination_reminders(cattle_list)
        )
        all_alerts.extend(
            await SchedulerService.check_health_reminders(cattle_list)
        )
        return all_alerts

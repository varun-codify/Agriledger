"""Email service (Stubbed - Zero Cost).

Previously used Resend. Completely stubbed to prevent runtime imports
and charges. Logs requests and reports success.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Zero-cost Stub service."""

    def __init__(self):
        pass

    @property
    def is_configured(self) -> bool:
        # The stub requires no external credentials and is always available.
        return True

    async def send_email(
        self,
        to: str | list[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        logger.info(f"Stub email request to {to} matching subject: {subject}")
        return True

    async def send_monthly_report(
        self,
        to: str,
        user_name: str,
        total_income: float,
        total_expenses: float,
        net_profit: float,
        report_pdf_path: Optional[str] = None,
    ) -> bool:
        logger.info(f"Stub monthly report request for {user_name} to {to}")
        return True

    async def send_breeding_alert(
        self,
        to: str,
        user_name: str,
        alert_type: str,
        animal_name: str,
        details: str,
    ) -> bool:
        logger.info(f"Stub breeding alert request to {to} for {animal_name}")
        return True

    async def send_weather_alert(
        self,
        to: str,
        user_name: str,
        alert_title: str,
        alert_message: str,
    ) -> bool:
        logger.info(f"Stub weather alert to {to}: {alert_title}")
        return True


# Global singleton
email_service = EmailService()

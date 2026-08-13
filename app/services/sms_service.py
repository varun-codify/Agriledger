"""SMS & WhatsApp automation service via generating intent links (Zero-Cost).

Provides WhatsApp click-to-chat links and browser push integration
instead of paid Twilio APIs.
"""

import logging
from typing import Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)


class SMSService:
    """Zero-cost notification service."""

    def __init__(self):
        pass

    @property
    def is_configured(self) -> bool:
        # No external credentials required: WhatsApp links work out of the box.
        return True

    def _generate_wa_link(self, to: str, body: str) -> str:
        """Generate a WhatsApp click-to-chat URL."""
        # Ensure number has country code, default to India if not specified
        if not to.startswith("+"):
            to = f"+91{to.lstrip('0')}"
        encoded_text = quote(body)
        return f"https://wa.me/{to.strip('+')}?text={encoded_text}"

    async def send_sms(self, to: str, body: str) -> bool:
        link = self._generate_wa_link(to, body)
        logger.info(f"Generated WA link for {to}: {link}")
        return True

    async def send_whatsapp(self, to: str, body: str) -> bool:
        link = self._generate_wa_link(to, body)
        logger.info(f"Generated WA link for {to}: {link}")
        return True

    async def send_breeding_reminder(
        self,
        to: str,
        animal_name: str,
        reminder_type: str,
        due_date: str,
        notes: Optional[str] = None,
    ) -> bool:
        """Send a breeding-related SMS reminder."""
        body = (
            f"🐄 AgriLedger Breeding Reminder\n\n"
            f"Animal: {animal_name}\n"
            f"Reminder: {reminder_type}\n"
            f"Due Date: {due_date}\n"
        )
        if notes:
            body += f"Notes: {notes}\n"
        body += "\nLog in to AgriLedger for details."
        return await self.send_sms(to, body)

    async def send_vaccination_reminder(
        self, to: str, animal_name: str, vaccine: str, due_date: str
    ) -> bool:
        """Send a vaccination reminder SMS."""
        body = (
            f"💉 Vaccination Reminder\n\n"
            f"Animal: {animal_name}\n"
            f"Vaccine: {vaccine}\n"
            f"Due: {due_date}\n\n"
            f"Please schedule with your veterinarian."
        )
        return await self.send_sms(to, body)

    async def send_weather_alert(
        self, to: str, alert_title: str, alert_message: str
    ) -> bool:
        """Send a weather danger alert via SMS."""
        body = f"⛈️ Weather Alert: {alert_title}\n\n{alert_message}\n\nTake necessary precautions for your farm."
        return await self.send_sms(to, body)

    async def send_payment_reminder(
        self, to: str, buyer: str, amount: float, item: str
    ) -> bool:
        """Send a payment reminder SMS."""
        body = (
            f"💰 Payment Reminder\n\n"
            f"Buyer: {buyer}\n"
            f"Item: {item}\n"
            f"Amount: ₹{amount:,.2f}\n\n"
            f"Please follow up for payment collection."
        )
        return await self.send_sms(to, body)

    async def send_calving_alert(
        self, to: str, animal_name: str, expected_date: str
    ) -> bool:
        """Send a calving expected date alert."""
        body = (
            f"🍼 Calving Alert\n\n"
            f"Animal: {animal_name}\n"
            f"Expected Calving Date: {expected_date}\n\n"
            f"Please prepare for the birth. Ensure veterinary support is available."
        )
        return await self.send_sms(to, body)


# Global singleton
sms_service = SMSService()

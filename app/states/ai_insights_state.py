"""AI-powered farm insights and conversational assistant.

Uses Google Gemini via the modern `google.genai` package, with an
intelligent rule-based fallback so the app keeps working without an API key.
"""

import datetime
import json
import logging

import reflex as rx
from google import genai
from google.genai import types

from app.config import config
from app.services.gemini_service import extract_json, retry_across_models
from app.states.cattle_state import CattleState
from app.states.crop_state import CropState
from app.states.transaction_state import TransactionState


class AIInsightsState(rx.State):
    """Manages AI-powered insights using Gemini or intelligent rule-based logic."""

    health_score: int = 85
    recommendations: list[dict] = [
        {
            "title": "Optimize Feed Mix",
            "desc": "Consider increasing protein content for lactating cows to boost milk yield by 5%.",
            "type": "optimization",
        },
        {
            "title": "Weather Alert",
            "desc": "Heavy rain expected next week. Ensure drainage systems are clear.",
            "type": "warning",
        },
    ]
    seasonal_tips: list[str] = [
        "Prepare for upcoming sowing season.",
        "Check vaccination schedules for calves.",
    ]
    is_loading: bool = False

    # Chatbot state
    chat_messages: list[dict] = []
    chat_input: str = ""
    chat_loading: bool = False

    def _client(self) -> genai.Client:
        """Build a Gemini client for the configured API key."""
        return genai.Client(api_key=config.gemini.api_key)

    @rx.event
    def set_chat_input(self, value: str):
        self.chat_input = value

    @rx.event
    def handle_chat_key(self, key: str):
        if key == "Enter":
            self.send_chat_message()

    @rx.event
    def ask_question(self, question: str):
        self.chat_input = question
        self.send_chat_message()

    @rx.event(background=True)
    async def send_chat_message(self):
        """Send a message to the AI chatbot and get a response."""
        if not self.chat_input.strip():
            return
        user_msg = self.chat_input.strip()
        async with self:
            self.chat_messages.append({"role": "user", "content": user_msg})
            self.chat_input = ""
            self.chat_loading = True

        # Gather farm context
        ts = await self.get_state(TransactionState)
        cs = await self.get_state(CattleState)
        crops = await self.get_state(CropState)

        total_income = sum(float(t["amount"]) for t in ts.transactions if t["type"] == "income")
        total_expense = sum(float(t["amount"]) for t in ts.transactions if t["type"] == "expense")
        total_animals = len(cs.cattle_list)
        sick_animals = sum(1 for c in cs.cattle_list if c.get("health_status") in ["Sick", "Under Treatment"])
        active_crops = len([c for c in crops.crops_list if c["status"] == "Growing"])

        farm_context = (
            f"Farm data: Total income=₹{total_income:,.2f}, Total expenses=₹{total_expense:,.2f}, "
            f"Net profit=₹{total_income - total_expense:,.2f}. "
            f"Animals: {total_animals} total ({sick_animals} sick). "
            f"Active crops: {active_crops}. "
            f"Milk sales this month: {len(ts.milk_sales)}, Coconut sales: {len(ts.coconut_sales)}. "
            f"Current month: {datetime.datetime.now().strftime('%B %Y')}."
        )

        bot_reply = None
        if config.gemini.is_configured:
            try:
                client = self._client()

                async def _run_chat(model: str):
                    chat = client.aio.chats.create(
                        model=model,
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "You are AgriLedger AI, a helpful farm management assistant. "
                                "Answer questions about the farmer's data concisely and practically. "
                                "Give specific, actionable advice. Keep responses under 100 words. "
                                f"Context: {farm_context}"
                            )
                        ),
                    )
                    response = await chat.send_message(user_msg)
                    return response.text.strip() if response.text else None

                bot_reply = await retry_across_models(_run_chat)
            except Exception as e:
                logging.exception(f"AI chat failed: {e}")
                bot_reply = None
        if not bot_reply:
            bot_reply = self._rule_based_response(
                user_msg, total_income, total_expense, sick_animals, total_animals
            )

        async with self:
            self.chat_messages.append({"role": "assistant", "content": bot_reply})
            self.chat_loading = False

    def _rule_based_response(self, question: str, income: float, expense: float, sick: int, total: int) -> str:
        """Fallback rule-based responses when Gemini is not available."""
        q = question.lower()
        profit = income - expense
        if "milk" in q and "drop" in q:
            return "Milk production drops can be caused by: heat stress, inadequate feed nutrition, dehydration, or health issues. Check your animals' health status and ensure they have adequate water and balanced feed."
        elif "feed cost" in q or "reduce" in q and "cost" in q:
            return f"Your current expenses are ₹{expense:,.2f}. To reduce feed costs: consider buying in bulk, growing your own fodder, optimizing feed ratios based on animal needs, and reducing waste."
        elif "crop" in q and "plant" in q:
            return "Choose crops based on your soil type, climate, and water availability. Consider crop rotation to maintain soil health. Local agricultural extension offices can provide region-specific recommendations."
        elif "profit" in q or "income" in q:
            return f"Your current net profit is ₹{profit:,.2f} (Income: ₹{income:,.2f}, Expenses: ₹{expense:,.2f}). {'This is healthy!' if profit > 0 else 'Expenses exceed income - review your spending categories.'}"
        elif "health" in q or "sick" in q:
            return f"You have {sick} sick animals out of {total}. {'Please check on them immediately and consult a veterinarian.' if sick > 0 else 'All animals appear healthy. Keep up with regular vaccinations.'}"
        elif "breeding" in q:
            return "Breeding success depends on: proper heat detection, timely insemination, nutrition, and health. Ensure cows are in good body condition (BCS 3-3.5) before breeding."
        else:
            return f"Based on your farm data: You have {total} animals, ₹{income:,.2f} income, and ₹{expense:,.2f} in expenses. For specific advice, try asking about milk production, feed costs, animal health, or crop planning."

    @rx.event(background=True)
    async def refresh_insights(self):
        async with self:
            self.is_loading = True
            ts = await self.get_state(TransactionState)
            cs = await self.get_state(CattleState)
            crops = await self.get_state(CropState)
        score = 100
        total_income = sum(
            (float(t["amount"]) for t in ts.transactions if t["type"] == "income")
        )
        total_expense = sum(
            (float(t["amount"]) for t in ts.transactions if t["type"] == "expense")
        )
        if total_income > 0:
            expense_ratio = total_expense / total_income
            if expense_ratio > 0.9:
                score -= 25
            elif expense_ratio > 0.7:
                score -= 15
            elif expense_ratio > 0.5:
                score -= 5
        elif total_expense > 0:
            score -= 30
        else:
            score -= 10
        total_animals = len(cs.cattle_list)
        sick_animals = sum(
            (
                1
                for c in cs.cattle_list
                if c.get("health_status") in ["Sick", "Under Treatment"]
            )
        )
        if total_animals > 0:
            sick_pct = sick_animals / total_animals
            if sick_pct > 0.2:
                score -= 30
            elif sick_pct > 0.1:
                score -= 20
            elif sick_pct > 0:
                score -= 10
        active_crops = len([c for c in crops.crops_list if c["status"] == "Growing"])
        if active_crops == 0 and len(crops.crops_list) > 0:
            score -= 10
        final_score = max(0, min(100, score))
        new_recs = []
        new_tips = []
        ai_success = False
        if config.gemini.is_configured:
            try:
                client = self._client()
                context = {
                    "financial": {"income": total_income, "expense": total_expense},
                    "cattle": {
                        "total": total_animals,
                        "sick": sick_animals,
                        "types": list(set((c["animal_type"] for c in cs.cattle_list))),
                    },
                    "crops": {"count": len(crops.crops_list), "active": active_crops},
                    "month": datetime.datetime.now().strftime("%B"),
                }
                prompt = (
                    f"Analyze this farm data: {json.dumps(context)}\n"
                    "Provide 3 concise insights/recommendations in JSON format.\n"
                    'JSON keys: "recommendations" (list of objects with "title", "desc", "type") and "seasonal_tips" (list of strings).\n'
                    'Type must be exactly one of: "optimization", "warning", "opportunity", "info".\n'
                    "Keep descriptions under 15 words. Use Indian Rupees (₹), never $."
                )
                async def _run_insights(model: str):
                    return await client.aio.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        ),
                    )

                response = await retry_across_models(_run_insights)
                if response:
                    result = extract_json(response.text) or {}
                    # Defensive: the model is asked for a JSON object, but guard
                    # every nested value so a wrong shape can never crash the UI.
                    raw_recs = result.get("recommendations")
                    if isinstance(raw_recs, list):
                        new_recs = [
                            {
                                **rec,
                                "type": (
                                    rec.get("type")
                                    if rec.get("type")
                                    in ("optimization", "warning", "opportunity", "info")
                                    else "info"
                                ),
                            }
                            for rec in raw_recs
                            if isinstance(rec, dict)
                        ]
                    raw_tips = result.get("seasonal_tips")
                    if isinstance(raw_tips, list):
                        new_tips = [str(t) for t in raw_tips if t]
                    ai_success = bool(result)
            except Exception as e:
                logging.exception(
                    f"AI Insights generation failed, falling back to rules: {e}"
                )
                ai_success = False
        if not ai_success:
            if total_expense > total_income and total_income > 0:
                new_recs.append(
                    {
                        "title": "Cost Control Needed",
                        "desc": "Expenses are higher than income. Review your recent spending.",
                        "type": "warning",
                    }
                )
            elif total_income > total_expense * 1.5:
                new_recs.append(
                    {
                        "title": "Healthy Profit Margin",
                        "desc": "Good financial health. Consider reinvesting in equipment.",
                        "type": "opportunity",
                    }
                )
            if sick_animals > 0:
                new_recs.append(
                    {
                        "title": "Sick Animals Alert",
                        "desc": f"{sick_animals} animals need attention. Check health logs immediately.",
                        "type": "warning",
                    }
                )
            elif total_animals > 0:
                new_recs.append(
                    {
                        "title": "Herd Health",
                        "desc": "Herd is healthy. Keep up with vaccination schedules.",
                        "type": "info",
                    }
                )
            if active_crops > 0:
                new_recs.append(
                    {
                        "title": "Active Growth",
                        "desc": f"{active_crops} crops are growing. Check soil moisture regularly.",
                        "type": "optimization",
                    }
                )
            if not new_recs:
                new_recs.append(
                    {
                        "title": "Data Needed",
                        "desc": "Add more farm data (cattle, crops, transactions) to get specific insights.",
                        "type": "info",
                    }
                )
            month = datetime.datetime.now().month
            if 3 <= month <= 5:
                new_tips = ["Prepare soil for planting.", "Inspect irrigation systems."]
            elif 6 <= month <= 8:
                new_tips = [
                    "Ensure water availability for livestock.",
                    "Monitor crops for pests.",
                ]
            elif 9 <= month <= 11:
                new_tips = ["Plan harvest logistics.", "Prepare barns for winter."]
            else:
                new_tips = ["Protect animals from cold.", "Maintain machinery."]
        async with self:
            self.health_score = final_score
            self.recommendations = new_recs
            self.seasonal_tips = new_tips
            self.is_loading = False

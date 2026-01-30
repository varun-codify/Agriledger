import reflex as rx
import os
import openai
import logging
import datetime
import json
from app.states.transaction_state import TransactionState
from app.states.cattle_state import CattleState
from app.states.crop_state import CropState


class AIInsightsState(rx.State):
    """Manages AI-powered insights using OpenAI or intelligent rule-based logic."""

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
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                client = openai.AsyncOpenAI(api_key=api_key)
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
                prompt = f'\n                Analyze this farm data: {json.dumps(context)}\n                Provide 3 concise insights/recommendations in JSON format.\n                JSON keys: "recommendations" (list of objects with "title", "desc", "type") and "seasonal_tips" (list of strings).\n                Type options: "optimization", "warning", "opportunity", "info".\n                Keep descriptions under 15 words.\n                '
                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=300,
                )
                result = json.loads(response.choices[0].message.content)
                if "recommendations" in result:
                    new_recs = result["recommendations"]
                if "seasonal_tips" in result:
                    new_tips = result["seasonal_tips"]
                ai_success = True
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
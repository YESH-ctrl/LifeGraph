from typing import Any, Dict, List
from engines.agents.base_agent import BaseAgent

class AdaptiveAgent(BaseAgent):
    """
    V2 Adaptive Agent – Persona Engine.
    Determines shopper persona from mission context, user history, cart size, and urgency.
    """

    PERSONA_INTERVENTIONS = {
        "Event Planner": "Suggest celebration essentials and quantity upgrades.",
        "Festival Shopper": "Highlight festival deals, bundles, and seasonal products.",
        "Monthly Grocery Shopper": "Recommend bulk purchases and subscription options.",
        "Travel Planner": "Suggest travel essentials, packing lists, and insurance.",
        "Student Shopper": "Focus on budget-friendly alternatives and study essentials.",
        "Health Focused Shopper": "Recommend organic, low-calorie, and wellness products.",
        "Emergency Buyer": "Prioritize fast delivery and essential items only.",
        "Research Buyer": "Provide detailed product comparisons and reviews.",
    }

    # Categories that map to specific personas
    EVENT_CATEGORIES = {"CELEBRATION", "EVENT", "PARTY", "WEDDING", "BIRTHDAY"}
    GROCERY_CATEGORIES = {"GROCERY", "COOKING", "FOOD", "KITCHEN"}
    HEALTH_CATEGORIES = {"HEALTH", "FITNESS", "WELLNESS", "MEDICAL"}
    TRAVEL_CATEGORIES = {"TRAVEL", "OUTDOOR", "CAMPING", "VACATION"}
    FESTIVAL_CATEGORIES = {"FESTIVAL", "DIWALI", "CHRISTMAS", "HOLI", "EID"}

    def __init__(self):
        super().__init__(name="AdaptiveAgent")

    def execute(self, action: str, payload: Any) -> Any:
        if action == "adapt":
            return self.adapt_rules(payload)
        elif action == "get_state":
            return self.get_adaptive_state(payload.get("user_id"))
        else:
            raise ValueError(f"Unknown action {action} for AdaptiveAgent")

    def _determine_persona(self, mission_category: str, cart_size: int,
                           urgency: str, completion_rate: float,
                           mission_count: int) -> str:
        """Determine shopper persona from mission context and user behavior."""
        category_upper = (mission_category or "").upper()

        # Emergency: urgency is HIGH regardless of category
        if urgency and urgency.upper() == "HIGH":
            return "Emergency Buyer"

        # Festival
        if category_upper in self.FESTIVAL_CATEGORIES:
            return "Festival Shopper"

        # Event / Celebration
        if category_upper in self.EVENT_CATEGORIES:
            return "Event Planner"

        # Health / Wellness
        if category_upper in self.HEALTH_CATEGORIES:
            return "Health Focused Shopper"

        # Travel
        if category_upper in self.TRAVEL_CATEGORIES:
            return "Travel Planner"

        # Monthly grocery: recurring patterns
        if category_upper in self.GROCERY_CATEGORIES and mission_count >= 3:
            return "Monthly Grocery Shopper"

        # Student: small budget signals (small cart + grocery)
        if category_upper in self.GROCERY_CATEGORIES and cart_size <= 5:
            return "Student Shopper"

        # Default
        return "Research Buyer"

    def adapt_rules(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriched adapt: uses mission_id context + user history to determine persona.
        Accepts:
          - user_id
          - mission_id (optional)
          - mission_category (optional)
          - cart_size (optional)
          - urgency (optional)
          - history (optional)
        """
        user_id = payload.get("user_id", "")
        mission_category = payload.get("mission_category", "")
        cart_size = int(payload.get("cart_size", 0))
        urgency = payload.get("urgency", "")
        history = payload.get("history", [])

        # Try to get mission category from graph if not provided
        if not mission_category and payload.get("mission_id"):
            try:
                from graph.service import GraphService
                gs = GraphService()
                metadata = gs.get_mission_metadata(payload["mission_id"])
                if metadata:
                    mission_category = metadata.get("category", "")
            except Exception:
                pass

        # Get user mission history to determine patterns
        mission_count = len(history)
        completion_rate = 0.0
        try:
            from domains.memory.service import MemoryService
            mem = MemoryService()
            mem_history = mem.get_mission_history(user_id)
            active = mem_history.get("active", [])
            completed = mem_history.get("completed", [])
            total = len(active) + len(completed)
            mission_count = max(mission_count, total)
            if total > 0:
                completion_rate = len(completed) / total
        except Exception:
            pass

        persona = self._determine_persona(
            mission_category=mission_category,
            cart_size=cart_size,
            urgency=urgency,
            completion_rate=completion_rate,
            mission_count=mission_count,
        )

        intervention = self.PERSONA_INTERVENTIONS.get(persona, "Provide general shopping guidance.")

        self.emit_event("RulesAdapted", {
            "user_id": user_id,
            "persona": persona,
            "mission_category": mission_category
        })

        return {
            "success": True,
            "shopper_type": persona,
            "recommended_intervention": intervention,
            "adapted_rules": {
                "strict_mode": urgency and urgency.upper() == "HIGH",
                "allow_substitution": True,
                "persona": persona,
            }
        }

    def get_adaptive_state(self, user_id: str) -> Dict[str, Any]:
        """Returns current adaptive state for a user."""
        try:
            from domains.memory.service import MemoryService
            mem = MemoryService()
            mem_history = mem.get_mission_history(user_id)
            active = mem_history.get("active", [])
            completed = mem_history.get("completed", [])
            total = len(active) + len(completed)
            completion_rate = len(completed) / total if total > 0 else 0.0
        except Exception:
            completion_rate = 0.0

        return {
            "user_id": user_id,
            "completion_rate": completion_rate,
        }

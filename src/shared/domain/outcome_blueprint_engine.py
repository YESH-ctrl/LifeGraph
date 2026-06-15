import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Single source of truth for outcome-based blueprints
MISSION_BLUEPRINTS = {
    "weight_loss_journey": {
        "required_groups": [
            "protein_source",
            "fiber_source",
            "healthy_fat",
            "hydration",
            "breakfast_option"
        ],
        "targets": {
            "protein": 80,
            "fiber": 30,
            "hydration_liters": 3,
            "processed_food_limit": 10
        }
    },
    "healthy_lifestyle_start": {
        "required_groups": [
            "balanced_macros",
            "whole_foods",
            "micronutrients",
            "healthy_snacks"
        ]
    },
    "healthy_eating": {
        "required_groups": [
            "balanced_macros",
            "whole_foods",
            "micronutrients",
            "healthy_snacks"
        ]
    },
    "monthly_grocery_refill": {
        "required_groups": [
            "staples",
            "household_consumables",
            "meal_ingredients"
        ]
    },
    "weekly_grocery_shopping": {
        "required_groups": [
            "staples",
            "household_consumables",
            "meal_ingredients"
        ]
    },
    "general_refill": {
        "required_groups": [
            "staples",
            "household_consumables",
            "meal_ingredients"
        ]
    },
    "chicken_biryani": {
        "required_groups": [
            "staples",
            "meal_ingredients"
        ]
    },
    "weekend_cooking_session": {
        "required_groups": [
            "staples",
            "meal_ingredients"
        ]
    }
}

class OutcomeBlueprintEngine:
    def get_blueprint(self, mission_id: str) -> Dict[str, Any]:
        """Returns the outcome blueprint targets and required groups for a mission."""
        bp = MISSION_BLUEPRINTS.get(mission_id)
        if bp is None:
            # Smart fallback blueprint for unknown or generic missions
            logger.info(f"Using default fallback outcome blueprint for mission: '{mission_id}'")
            return {
                "required_groups": [
                    "staples",
                    "meal_ingredients"
                ]
            }
        return bp

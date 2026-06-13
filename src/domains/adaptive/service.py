from datetime import datetime, timezone
from domains.adaptive.repository import AdaptiveRepository
from domains.adaptive.models import AdaptiveProfileModel
from domains.memory.service import MemoryService

class AdaptiveService:
    """Service handling business logic for the adaptive domain."""

    def __init__(self):
        self.repository = AdaptiveRepository()
        self.memory_service = MemoryService()

    def determine_shopper_type(self, completion_rate: float, preferred_budget: str) -> str:
        if completion_rate >= 0.8 and preferred_budget == "LOW":
            return "MISSION_DRIVEN"
        if completion_rate < 0.5:
            return "EXPLORER"
        return "BALANCED"

    def calculate_intervention_mode(self, shopper_type: str) -> str:
        if shopper_type == "MISSION_DRIVEN":
            return "STRICT"
        if shopper_type == "EXPLORER":
            return "FLEXIBLE"
        return "MODERATE"

    def analyze_user_behavior(self, user_id: str) -> AdaptiveProfileModel:
        """Analyzes behavior using memory domain data."""
        history = self.memory_service.get_mission_history(user_id)
        active_missions = history.get("active", [])
        completed_missions = history.get("completed", [])

        total_missions = len(active_missions) + len(completed_missions)
        completion_rate = 0.0
        behavior_score = 0.0

        if total_missions > 0:
            completion_rate = len(completed_missions) / total_missions
            behavior_score = completion_rate

        profile = self.memory_service.get_user_profile(user_id)
        preferences = profile.preferences if hasattr(profile, 'preferences') and profile.preferences else {}
        preferred_budget = preferences.get("preferredBudget", "UNKNOWN").upper()

        shopper_type = self.determine_shopper_type(completion_rate, preferred_budget)
        intervention_mode = self.calculate_intervention_mode(shopper_type)

        adaptive_profile = AdaptiveProfileModel(
            user_id=user_id,
            shopper_type=shopper_type,
            intervention_mode=intervention_mode,
            behavior_score=behavior_score,
            last_analyzed=datetime.now(timezone.utc).isoformat()
        )

        return self.repository.save_profile(adaptive_profile)

    def get_shopper_profile(self, user_id: str) -> AdaptiveProfileModel:
        """Gets the adaptive profile for a user."""
        profile = self.repository.get_profile(user_id)
        if not profile:
            return self.analyze_user_behavior(user_id)
        return profile

    def build_adaptive_decision(self, user_id: str) -> dict:
        """Builds a decision context based on the profile."""
        profile = self.get_shopper_profile(user_id)
        return {
            "shopper_type": profile.shopper_type,
            "intervention_mode": profile.intervention_mode,
            "score": profile.behavior_score
        }

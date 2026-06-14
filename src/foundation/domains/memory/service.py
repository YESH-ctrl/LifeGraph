from typing import List, Dict, Any
from datetime import datetime, timezone
from foundation.domains.memory.repository import MemoryRepository
from foundation.domains.memory.models import MemoryProfileModel, MissionMemoryModel
from foundation.domains.memory.schemas import MissionStateRequest, MemoryProfileRequest

class MemoryService:
    """Service handling business logic for the memory domain."""
    
    def __init__(self):
        self.repository = MemoryRepository()

    def get_user_profile(self, user_id: str) -> MemoryProfileModel:
        profile = self.repository.get_profile(user_id)
        if not profile:
            return MemoryProfileModel(user_id=user_id)
        return profile

    def upsert_user_profile(self, data: MemoryProfileRequest) -> MemoryProfileModel:
        profile = MemoryProfileModel(
            user_id=data.user_id,
            preferences=data.preferences,
            adaptive_score=data.adaptive_score,
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        return self.repository.upsert_profile(profile)

    def track_mission(self, data: MissionStateRequest) -> MissionMemoryModel:
        """Tracks the state of a mission."""
        completed_at = ""
        if data.status == "COMPLETED":
            completed_at = datetime.now(timezone.utc).isoformat()
            
        mission = MissionMemoryModel(
            user_id=data.user_id,
            mission_id=data.mission_id,
            mission_name=data.mission_name,
            status=data.status,
            completed_at=completed_at
        )
        return self.repository.save_mission_state(mission)

    def get_active_missions(self, user_id: str) -> List[MissionMemoryModel]:
        """Gets active missions for a user."""
        return self.repository.query_missions(user_id, status_filter="ACTIVE")

    def get_completed_missions(self, user_id: str) -> List[MissionMemoryModel]:
        """Gets completed missions for a user."""
        return self.repository.query_missions(user_id, status_filter="COMPLETED")

    def get_mission_history(self, user_id: str) -> Dict[str, List[MissionMemoryModel]]:
        """Gets the complete mission history for a user."""
        missions = self.repository.query_missions(user_id)
        active = [m for m in missions if m.status == "ACTIVE"]
        completed = [m for m in missions if m.status == "COMPLETED"]
        return {"active": active, "completed": completed}

    def build_adaptive_context(self, user_id: str) -> Dict[str, Any]:
        """Builds a full context from the entire memory partition."""
        items = self.repository.get_full_memory_context(user_id)
        profile = None
        missions = []
        
        for item in items:
            if item.get("SK") == "PROFILE":
                profile = MemoryProfileModel.from_dict(item).to_dict()
            elif item.get("SK", "").startswith("MISSION#"):
                missions.append(MissionMemoryModel.from_dict(item).to_dict())
                
        return {
            "profile": profile,
            "missions": missions
        }

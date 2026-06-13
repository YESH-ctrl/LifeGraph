from typing import List, Optional, Dict, Any
from infrastructure.dynamodb.base_repository import BaseRepository
from domains.memory.models import MemoryProfileModel, MissionMemoryModel

class MemoryRepository(BaseRepository):
    """Repository for managing memory data in DynamoDB."""
    
    def get_profile(self, user_id: str) -> Optional[MemoryProfileModel]:
        item = self.get_item(f"MEMORY#{user_id}", "PROFILE")
        if item:
            return MemoryProfileModel.from_dict(item)
        return None

    def upsert_profile(self, profile: MemoryProfileModel) -> MemoryProfileModel:
        self.put_item(profile.to_dict())
        return profile

    def save_mission_state(self, mission: MissionMemoryModel) -> MissionMemoryModel:
        """Saves a mission state to DynamoDB."""
        self.put_item(mission.to_dict())
        return mission

    def query_missions(self, user_id: str, status_filter: Optional[str] = None) -> List[MissionMemoryModel]:
        items = self.query_by_pk(f"MEMORY#{user_id}", "MISSION#")
        missions = [MissionMemoryModel.from_dict(item) for item in items]
        if status_filter:
            missions = [m for m in missions if m.status == status_filter]
        return missions

    def get_full_memory_context(self, user_id: str) -> List[Dict[str, Any]]:
        return self.query_by_pk(f"MEMORY#{user_id}")

from typing import List, Optional, Dict, Any
from foundation.infrastructure.dynamodb.base_repository import BaseRepository
from foundation.domains.memory.models import MemoryProfileModel, MissionMemoryModel

class MemoryRepository(BaseRepository):
    """Repository for managing memory data in DynamoDB."""
    
    def get_profile(self, user_id: str) -> Optional[MemoryProfileModel]:
        item = self.get_item(f"USER#{user_id}", "PROFILE")
        if not item:
            item = self.get_item(f"MEMORY#{user_id}", "PROFILE")
        if item:
            return MemoryProfileModel.from_dict(item)
        return None

    def upsert_profile(self, profile: MemoryProfileModel) -> MemoryProfileModel:
        # Save V2: USER#<user_id> / PROFILE
        profile_dict = profile.to_dict()
        self.put_item(profile_dict)
        
        # Dual-write V1: MEMORY#<user_id> / PROFILE
        legacy_dict = profile_dict.copy()
        legacy_dict['PK'] = f"MEMORY#{profile.user_id}"
        self.put_item(legacy_dict)
        return profile

    def save_mission_state(self, mission: MissionMemoryModel) -> MissionMemoryModel:
        """Saves a mission state to DynamoDB (writes to both USER# V2 and MEMORY# V1)."""
        mission_dict = mission.to_dict()
        self.put_item(mission_dict)
        
        # Dual-write legacy V1 structure
        legacy_dict = mission_dict.copy()
        legacy_dict['PK'] = f"MEMORY#{mission.user_id}"
        legacy_dict['SK'] = f"MISSION#{mission.mission_id}"
        self.put_item(legacy_dict)
        return mission

    def query_missions(self, user_id: str, status_filter: Optional[str] = None) -> List[MissionMemoryModel]:
        # Try query V2 first
        items = self.query_by_pk(f"USER#{user_id}", "MISSION#")
        if not items:
            # Fallback to V1
            items = self.query_by_pk(f"MEMORY#{user_id}", "MISSION#")
            
        missions = [MissionMemoryModel.from_dict(item) for item in items]
        if status_filter:
            missions = [m for m in missions if m.status == status_filter]
        return missions

    def get_full_memory_context(self, user_id: str) -> List[Dict[str, Any]]:
        # Query USER# first
        items = self.query_by_pk(f"USER#{user_id}")
        if not items or len(items) <= 1: # If only PROFILE or empty, check MEMORY#
            legacy_items = self.query_by_pk(f"MEMORY#{user_id}")
            if len(legacy_items) > len(items):
                return legacy_items
        return items

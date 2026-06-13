from typing import List, Optional
from infrastructure.dynamodb.base_repository import BaseRepository
from domains.memory.models import MemoryModel

class MemoryRepository(BaseRepository):
    """Repository for managing memory data in DynamoDB."""
    
    def save_mission_state(self, memory: MemoryModel) -> MemoryModel:
        """Saves a mission state to DynamoDB."""
        raise NotImplementedError("save_mission_state is not implemented.")

    def query_active_missions(self, user_id: str) -> List[MemoryModel]:
        """Queries active missions for a given user."""
        raise NotImplementedError("query_active_missions is not implemented.")

    def query_completed_missions(self, user_id: str) -> List[MemoryModel]:
        """Queries completed missions for a given user."""
        raise NotImplementedError("query_completed_missions is not implemented.")

    def get_mission_history(self, user_id: str) -> List[MemoryModel]:
        """Retrieves the full mission history for a given user."""
        raise NotImplementedError("get_mission_history is not implemented.")

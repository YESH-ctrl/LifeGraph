from typing import List
from foundation.domains.memory.repository import MemoryRepository
from foundation.domains.memory.models import MemoryModel
from foundation.domains.memory.schemas import MissionStateRequest

class MemoryService:
    """Service handling business logic for the memory domain."""
    
    def __init__(self):
        self.repository = MemoryRepository()

    def track_mission(self, data: MissionStateRequest) -> MemoryModel:
        """Tracks the state of a mission."""
        raise NotImplementedError("track_mission is not implemented.")

    def get_active_missions(self, user_id: str) -> List[MemoryModel]:
        """Gets active missions for a user."""
        raise NotImplementedError("get_active_missions is not implemented.")

    def get_completed_missions(self, user_id: str) -> List[MemoryModel]:
        """Gets completed missions for a user."""
        raise NotImplementedError("get_completed_missions is not implemented.")

    def get_mission_history(self, user_id: str) -> List[MemoryModel]:
        """Gets the complete mission history for a user."""
        raise NotImplementedError("get_mission_history is not implemented.")

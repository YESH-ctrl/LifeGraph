from typing import List, Any
from agents.base_agent import BaseAgent
from shared.repositories.mission_repository import MissionRepository
from shared.models.mission_model import MissionModel
from shared.schemas.mission_schemas import MissionCreate, MissionUpdate
from core.exceptions import NotFoundException

class MissionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MissionAgent")
        self.repository = MissionRepository()

    def execute(self, action: str, payload: Any) -> Any:
        """Route to appropriate action."""
        if action == "create":
            return self.create_mission(payload)
        elif action == "get":
            return self.get_mission(payload)
        elif action == "update":
            return self.update_mission(payload.get("mission_id"), payload.get("data"))
        elif action == "delete":
            return self.delete_mission(payload)
        elif action == "list":
            return self.list_missions()
        else:
            raise ValueError(f"Unknown action {action} for MissionAgent")

    def create_mission(self, data: MissionCreate) -> MissionModel:
        mission = MissionModel(
            mission_id=data.mission_id, 
            name=data.name, 
            description=data.description, 
            category=data.category
        )
        saved = self.repository.create_mission(mission)
        self.emit_event("MissionCreated", {"mission_id": saved.mission_id})
        return saved

    def get_mission(self, mission_id: str) -> MissionModel:
        mission = self.repository.get_mission(mission_id)
        if not mission:
            raise NotFoundException("Mission", mission_id)
        return mission

    def update_mission(self, mission_id: str, data: MissionUpdate) -> MissionModel:
        mission = self.get_mission(mission_id)
        if data.name is not None:
            mission.name = data.name
        if data.description is not None:
            mission.description = data.description
        if data.category is not None:
            mission.category = data.category
        return self.repository.update_mission(mission)

    def delete_mission(self, mission_id: str) -> None:
        self.get_mission(mission_id) # Check existence
        self.repository.delete_mission(mission_id)
        self.emit_event("MissionDeleted", {"mission_id": mission_id})

    def list_missions(self) -> List[MissionModel]:
        return self.repository.list_missions()

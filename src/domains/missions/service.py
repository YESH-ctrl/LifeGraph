from typing import List
from domains.missions.repository import MissionRepository
from domains.missions.models import MissionModel
from domains.missions.schemas import MissionCreate, MissionUpdate
from core.exceptions import NotFoundException

class MissionService:
    def __init__(self):
        self.repository = MissionRepository()

    def create_mission(self, data: MissionCreate) -> MissionModel:
        mission = MissionModel(
            mission_id=data.mission_id, 
            name=data.name, 
            description=data.description, 
            category=data.category
        )
        return self.repository.create_mission(mission)

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

    def list_missions(self) -> List[MissionModel]:
        return self.repository.list_missions()

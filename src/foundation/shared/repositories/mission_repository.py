from typing import Optional, List
from foundation.infrastructure.dynamodb.base_repository import BaseRepository
from foundation.shared.models.mission_model import MissionModel

class MissionRepository(BaseRepository):
    def create_mission(self, mission: MissionModel) -> MissionModel:
        self.put_item(mission.to_dict())
        return mission

    def get_mission(self, mission_id: str) -> Optional[MissionModel]:
        item = self.get_item(f"MISSION#{mission_id}", "METADATA")
        if item:
            return MissionModel.from_dict(item)
        return None

    def update_mission(self, mission: MissionModel) -> MissionModel:
        self.put_item(mission.to_dict())
        return mission

    def delete_mission(self, mission_id: str) -> None:
        self.delete_item(f"MISSION#{mission_id}", "METADATA")

    def list_missions(self) -> List[MissionModel]:
        items = self.scan_prefix("MISSION#", "METADATA")
        return [MissionModel.from_dict(item) for item in items]

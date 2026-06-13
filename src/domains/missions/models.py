from typing import Dict, Any

class MissionModel:
    def __init__(self, mission_id: str, name: str, description: str, category: str):
        self.mission_id = mission_id
        self.name = name
        self.description = description
        self.category = category

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MissionModel':
        return cls(
            mission_id=data.get('missionId', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            category=data.get('category', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'PK': f"MISSION#{self.mission_id}",
            'SK': "METADATA",
            'missionId': self.mission_id,
            'name': self.name,
            'description': self.description,
            'category': self.category
        }

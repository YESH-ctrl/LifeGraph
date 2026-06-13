from typing import Dict, Any

class MemoryModel:
    """Domain model representing a mission memory in DynamoDB."""
    
    def __init__(self, id: str, user_id: str, mission_id: str, mission_name: str, status: str, completed_at: str = ""):
        self.id = id
        self.user_id = user_id
        self.mission_id = mission_id
        self.mission_name = mission_name
        self.status = status
        self.completed_at = completed_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryModel':
        """Creates a MemoryModel from a DynamoDB dictionary representation."""
        return cls(
            id=data.get('id', ''),
            user_id=data.get('user_id', ''),
            mission_id=data.get('mission_id', ''),
            mission_name=data.get('mission_name', ''),
            status=data.get('status', ''),
            completed_at=data.get('completed_at', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the MemoryModel to a dictionary for DynamoDB storage."""
        return {
            'PK': f"USER#{self.user_id}",
            'SK': f"MEMORY#{self.mission_id}",
            'id': self.id,
            'user_id': self.user_id,
            'mission_id': self.mission_id,
            'mission_name': self.mission_name,
            'status': self.status,
            'completed_at': self.completed_at
        }

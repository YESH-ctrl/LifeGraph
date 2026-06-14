from typing import Dict, Any, Optional

class MemoryProfileModel:
    """Domain model representing a user's memory profile in DynamoDB."""
    def __init__(self, user_id: str, preferences: Optional[Dict[str, Any]] = None, adaptive_score: float = 0.0, updated_at: str = ""):
        self.user_id = user_id
        self.preferences = preferences or {}
        self.adaptive_score = adaptive_score
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryProfileModel':
        return cls(
            user_id=data.get('user_id', '') or (data.get('PK', '').split('#')[1] if 'USER#' in data.get('PK', '') or 'MEMORY#' in data.get('PK', '') else ''),
            preferences=data.get('preferences', {}),
            adaptive_score=float(data.get('adaptive_score', 0.0)),
            updated_at=data.get('updated_at', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'PK': f"USER#{self.user_id}",
            'SK': "PROFILE",
            'user_id': self.user_id,
            'preferences': self.preferences,
            'adaptive_score': self.adaptive_score,
            'updated_at': self.updated_at
        }

class MissionMemoryModel:
    """Domain model representing a mission memory in DynamoDB."""
    def __init__(self, user_id: str, mission_id: str, mission_name: str, status: str, completed_at: str = ""):
        self.user_id = user_id
        self.mission_id = mission_id
        self.mission_name = mission_name
        self.status = status
        self.completed_at = completed_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MissionMemoryModel':
        sk = data.get('SK', '')
        status = data.get('status', '')
        mission_id = data.get('mission_id', '')
        if not status:
            if 'ACTIVE' in sk:
                status = 'ACTIVE'
            elif 'COMPLETED' in sk:
                status = 'COMPLETED'
            else:
                status = 'ACTIVE'
        if not mission_id:
            parts = sk.split('#')
            if len(parts) >= 3:
                mission_id = parts[2]
            elif len(parts) >= 2:
                mission_id = parts[1]

        return cls(
            user_id=data.get('user_id', '') or (data.get('PK', '').split('#')[1] if 'USER#' in data.get('PK', '') or 'MEMORY#' in data.get('PK', '') else ''),
            mission_id=mission_id,
            mission_name=data.get('mission_name', '') or data.get('missionId', '') or mission_id,
            status=status,
            completed_at=data.get('completed_at', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        status_str = "ACTIVE" if self.status == "ACTIVE" else "COMPLETED"
        return {
            'PK': f"USER#{self.user_id}",
            'SK': f"MISSION#{status_str}#{self.mission_id}",
            'user_id': self.user_id,
            'mission_id': self.mission_id,
            'mission_name': self.mission_name,
            'status': self.status,
            'completed_at': self.completed_at
        }

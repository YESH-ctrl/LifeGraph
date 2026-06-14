import base64
from typing import Dict, Any

class RelationshipModel:
    def __init__(self, source_type: str, source_id: str, target_type: str, target_id: str, relationship_type: str):
        self.source_type = source_type
        self.source_id = source_id
        self.target_type = target_type
        self.target_id = target_id
        self.relationship_type = relationship_type

    @property
    def pk(self) -> str:
        return f"{self.source_type}#{self.source_id}"

    @property
    def sk(self) -> str:
        return f"{self.relationship_type}#{self.target_type}#{self.target_id}"

    @property
    def id(self) -> str:
        combined = f"{self.pk}::{self.sk}"
        return base64.urlsafe_b64encode(combined.encode()).decode()

    @classmethod
    def from_id(cls, relationship_id: str) -> tuple[str, str]:
        decoded = base64.urlsafe_b64decode(relationship_id.encode()).decode()
        pk, sk = decoded.split("::")
        return pk, sk

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipModel':
        # Reconstruct from PK/SK
        pk = data.get('PK', '')
        sk = data.get('SK', '')
        
        # PK format: SOURCE_TYPE#SOURCE_ID
        source_type, source_id = pk.split('#', 1)
        
        # SK format: REL_TYPE#TARGET_TYPE#TARGET_ID
        parts = sk.split('#', 2)
        relationship_type = parts[0]
        target_type = parts[1]
        target_id = parts[2]

        return cls(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relationship_type=relationship_type
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'PK': self.pk,
            'SK': self.sk,
            'sourceType': self.source_type,
            'sourceId': self.source_id,
            'targetType': self.target_type,
            'targetId': self.target_id,
            'relationshipType': self.relationship_type
        }

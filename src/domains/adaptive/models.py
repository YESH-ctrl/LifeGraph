from typing import Dict, Any
from decimal import Decimal

class AdaptiveProfileModel:
    """Domain model representing an adaptive shopper profile in DynamoDB."""
    def __init__(self, user_id: str, shopper_type: str, intervention_mode: str, behavior_score: float, last_analyzed: str = ""):
        self.user_id = user_id
        self.shopper_type = shopper_type
        self.intervention_mode = intervention_mode
        self.behavior_score = behavior_score
        self.last_analyzed = last_analyzed

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdaptiveProfileModel':
        return cls(
            user_id=data.get('user_id', ''),
            shopper_type=data.get('shopper_type', ''),
            intervention_mode=data.get('intervention_mode', ''),
            behavior_score=float(data.get('behavior_score', 0.0)),
            last_analyzed=data.get('last_analyzed', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'PK': f"ADAPTIVE#{self.user_id}",
            'SK': "PROFILE",
            'user_id': self.user_id,
            'shopper_type': self.shopper_type,
            'intervention_mode': self.intervention_mode,
            'behavior_score': Decimal(str(self.behavior_score)),
            'last_analyzed': self.last_analyzed
        }

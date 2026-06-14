from typing import Dict, Any

class SimulationModel:
    """Domain model representing a mission simulation in DynamoDB."""
    def __init__(self, simulation_id: str, user_id: str, mission_id: str, cart_id: str, 
                 success_probability: int, missing_items: list, predicted_outcome: str, created_at: str = ""):
        self.simulation_id = simulation_id
        self.user_id = user_id
        self.mission_id = mission_id
        self.cart_id = cart_id
        self.success_probability = success_probability
        self.missing_items = missing_items or []
        self.predicted_outcome = predicted_outcome
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationModel':
        return cls(
            simulation_id=data.get('simulation_id', ''),
            user_id=data.get('user_id', ''),
            mission_id=data.get('mission_id', ''),
            cart_id=data.get('cart_id', ''),
            success_probability=int(data.get('success_probability', 0)),
            missing_items=data.get('missing_items', []),
            predicted_outcome=data.get('predicted_outcome', ''),
            created_at=data.get('created_at', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'PK': f"SIMULATION#{self.simulation_id}",
            'SK': "METADATA",
            'GSI1PK': f"USER#{self.user_id}",
            'GSI1SK': f"SIMULATION#{self.simulation_id}",
            'simulation_id': self.simulation_id,
            'user_id': self.user_id,
            'mission_id': self.mission_id,
            'cart_id': self.cart_id,
            'success_probability': self.success_probability,
            'missing_items': self.missing_items,
            'predicted_outcome': self.predicted_outcome,
            'created_at': self.created_at
        }

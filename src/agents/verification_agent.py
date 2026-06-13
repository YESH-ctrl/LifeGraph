from typing import Any
from datetime import datetime
from agents.base_agent import BaseAgent
from shared.schemas.engine_schemas import VerificationRequest, VerificationResponseData
from shared.events import MissionVerifiedEvent
from infrastructure.dynamodb.base_repository import BaseRepository

class VerificationRepository(BaseRepository):
    pass

class VerificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="VerificationAgent")
        self.repository = VerificationRepository()

    def execute(self, action: str, payload: Any) -> Any:
        if action == "verify":
            return self.verify(payload)
        else:
            raise ValueError(f"Unknown action {action} for VerificationAgent")

    def verify(self, data: VerificationRequest) -> VerificationResponseData:
        """
        Business Logic:
        * Compare mission requirements against cart contents.
        * Calculate verification_score.
        """
        # Mock mission requirements for "BIRTHDAY"
        mission_requirements = ["Cake", "Candles", "Drinks", "Snacks"]
        
        # Mock cart contents
        cart_contents = ["Cake", "Balloons", "Drinks"]
        
        missing_items = []
        verification_score = 100
        
        for req in mission_requirements:
            if req not in cart_contents:
                missing_items.append(req)
                verification_score -= 25 # deduct 25 for each missing item
                
        # Prevent negative score
        verification_score = max(0, verification_score)
            
        res_data = VerificationResponseData(
            verification_score=verification_score,
            missing_items=missing_items
        )

        # Emit MissionVerifiedEvent
        event = MissionVerifiedEvent(
            mission_id=data.missionId,
            user_id="UNKNOWN_USER",  # Placeholder since request only contains missionId and cartId
            status="VERIFIED" if verification_score >= 70 else "FAILED",
            verified_at=datetime.utcnow().isoformat()
        )
        self.emit_event("MissionVerifiedEvent", event.dict())
        
        return res_data

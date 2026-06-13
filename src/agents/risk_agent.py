from typing import Any
from datetime import datetime
from agents.base_agent import BaseAgent
from shared.schemas.engine_schemas import RiskRequest, RiskResponseData
from shared.events import RiskCalculatedEvent
from infrastructure.dynamodb.base_repository import BaseRepository

class RiskRepository(BaseRepository):
    pass

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="RiskAgent")
        self.repository = RiskRepository()

    def execute(self, action: str, payload: Any) -> Any:
        if action == "analyze":
            return self.analyze(payload)
        else:
            raise ValueError(f"Unknown action {action} for RiskAgent")

    def analyze(self, data: RiskRequest) -> RiskResponseData:
        """
        Business Logic:
        * Calculate risk score.
        * Return LOW/MEDIUM/HIGH internally or as components.
        """
        risk_score = 0
        compatibility_risk = "LOW"
        budget_risk = "LOW"
        quantity_risk = "LOW"
        timing_risk = "LOW"
        
        # Mock logic based on verification results
        if data.verification_score < 50:
            risk_score += 50
            compatibility_risk = "HIGH"
        elif data.verification_score < 80:
            risk_score += 20
            compatibility_risk = "MEDIUM"
            
        if len(data.missing_items) > 2:
            quantity_risk = "HIGH"
            risk_score += 15
            
        res_data = RiskResponseData(
            compatibility_risk=compatibility_risk,
            budget_risk=budget_risk,
            quantity_risk=quantity_risk,
            timing_risk=timing_risk,
            risk_score=risk_score
        )

        # Emit RiskCalculatedEvent
        status = "risky" if risk_score >= 70 else ("suspicious" if risk_score >= 30 else "safe")
        event = RiskCalculatedEvent(
            user_id="UNKNOWN_USER",
            cart_id="UNKNOWN_CART",
            score=float(risk_score),
            status=status,
            calculated_at=datetime.utcnow().isoformat()
        )
        self.emit_event("RiskCalculatedEvent", event.dict())

        return res_data

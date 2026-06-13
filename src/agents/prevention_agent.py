from typing import Any
from datetime import datetime
from agents.base_agent import BaseAgent
from shared.schemas.engine_schemas import PreventionRequest, PreventionResponseData
from shared.events import CheckoutBlockedEvent
from infrastructure.dynamodb.base_repository import BaseRepository

class PreventionRepository(BaseRepository):
    pass

class PreventionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="PreventionAgent")
        self.repository = PreventionRepository()

    def execute(self, action: str, payload: Any) -> Any:
        if action == "evaluate":
            return self.evaluate(payload)
        else:
            raise ValueError(f"Unknown action {action} for PreventionAgent")

    def evaluate(self, data: PreventionRequest) -> PreventionResponseData:
        """
        Business Logic:
        * Decide allowCheckout based on verification and risk.
        * Return reason / warnings.
        """
        # Mocking downstream responses for now
        mock_verification_score = 60 # Assume MEDIUM risk from this
        mock_risk_score = 35 # Assume MEDIUM risk
        
        allow_checkout = True
        reason = ""
        
        if mock_risk_score >= 70 or mock_verification_score < 30:
            allow_checkout = False
            reason = "High risk or low verification score detected. Checkout blocked."
        elif mock_risk_score >= 30:
            reason = "Medium risk detected. Please review your cart."
            
        res_data = PreventionResponseData(
            allow_checkout=allow_checkout,
            reason=reason
        )

        # Emit CheckoutBlockedEvent if blocked
        if not allow_checkout:
            event = CheckoutBlockedEvent(
                user_id="UNKNOWN_USER",
                cart_id=data.cartId,
                reason=reason,
                blocked_at=datetime.utcnow().isoformat()
            )
            self.emit_event("CheckoutBlockedEvent", event.dict())

        return res_data

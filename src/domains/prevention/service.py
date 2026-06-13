from domains.prevention.repository import PreventionRepository
from domains.prevention.schemas import PreventionRequest, PreventionResponseData

class PreventionService:
    def __init__(self):
        self.repository = PreventionRepository()

    def evaluate(self, data: PreventionRequest) -> PreventionResponseData:
        """
        Business Logic:
        * Decide allowCheckout based on verification and risk.
        * Return reason / warnings.
        """
        # TODO: Integrate with Cart APIs, Verification APIs, and Risk APIs
        
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
            
        return PreventionResponseData(
            allow_checkout=allow_checkout,
            reason=reason
        )

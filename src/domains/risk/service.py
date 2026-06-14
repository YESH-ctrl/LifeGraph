from domains.risk.repository import RiskRepository
from domains.risk.schemas import RiskRequest, RiskResponseData
from domains.graph.service import GraphService

class RiskService:
    def __init__(self):
        self.repository = RiskRepository()
        self.graph_service = GraphService()

    def analyze(self, data: RiskRequest) -> RiskResponseData:
        """
        Business Logic:
        * Calculate risk score.
        * Return LOW/MEDIUM/HIGH internally or as components.
        """
        risk_score = 0
        compatibility_risk = 10
        budget_risk = 10
        quantity_risk = 10
        timing_risk = 10
        
        # Base logic on verification results
        if data.verification_score < 50:
            risk_score += 50
        elif data.verification_score < 80:
            risk_score += 20
            
        if len(data.missing_items) > 2:
            quantity_risk = 90
            risk_score += 15
            
        # Use graph data to infer compatibility and deep dependency risk
        has_deep_dependencies = False
        for missing_item in data.missing_items:
            # We fetch dependencies for the missing items.
            # If a missing item itself has dependencies, it means the user is missing a complex set of products.
            dependencies = self.graph_service.get_product_dependencies(missing_item)
            if len(dependencies) > 0:
                has_deep_dependencies = True
                risk_score += (10 * len(dependencies))
                
        if has_deep_dependencies:
            compatibility_risk = 90
        elif risk_score >= 50:
            compatibility_risk = 50
            
        # Ensure risk_score is capped at 100
        risk_score = min(100, risk_score)
            
        return RiskResponseData(
            compatibility_risk=compatibility_risk,
            budget_risk=budget_risk,
            quantity_risk=quantity_risk,
            timing_risk=timing_risk,
            risk_score=risk_score
        )

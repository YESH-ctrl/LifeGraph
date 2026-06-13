from typing import Dict, Any, List
from agents.orchestrator.schemas import (
    MissionExecutionResponse,
    MissionInfo,
    VerificationResult,
    RiskResult,
    SimulationResult,
    AdaptiveDecision,
    CheckoutDecision,
    RecommendationItem
)

class ResponseBuilder:
    @staticmethod
    def build_response(state: Dict[str, Any]) -> MissionExecutionResponse:
        """Accumulates status fields from the workflow execution state to build the final response schema."""
        
        # 1. Mission Info
        mission_data = state.get("mission_data", {})
        mission_info = MissionInfo(
            missionId=mission_data.get("mission_id", state.get("missionId", "")),
            name=mission_data.get("name", "Unknown Mission")
        )
        
        # 2. Verification
        verification_data = state.get("verification_data", {})
        verification_res = VerificationResult(
            score=verification_data.get("verification_score", 0),
            missingItems=verification_data.get("missing_items", [])
        )
        
        # 3. Risk
        risk_data = state.get("risk_data", {})
        risk_score = risk_data.get("risk_score", 0)
        overall_risk = "LOW"
        if risk_score >= 70:
            overall_risk = "HIGH"
        elif risk_score >= 30:
            overall_risk = "MEDIUM"
            
        risk_res = RiskResult(
            overallRisk=overall_risk,
            compatibilityRisk=int(risk_score),  # Mock / aggregate mapping
            budgetRisk=0 if risk_data.get("budget_risk") == "LOW" else (15 if risk_data.get("budget_risk") == "MEDIUM" else 50),
            quantityRisk=0 if risk_data.get("quantity_risk") == "LOW" else (15 if risk_data.get("quantity_risk") == "MEDIUM" else 50),
            timingRisk=0 if risk_data.get("timing_risk") == "LOW" else (15 if risk_data.get("timing_risk") == "MEDIUM" else 50)
        )
        
        # 4. Simulation
        simulation_data = state.get("simulation_data", {})
        sim_details = simulation_data.get("details", {})
        success_probability = int(sim_details.get("predicted_satisfaction", 0.85) * 100)
        simulation_res = SimulationResult(
            successProbability=success_probability
        )
        
        # 5. Adaptive Decision
        adaptive_data = state.get("adaptive_data", {})
        strict_mode = adaptive_data.get("adapted_rules", {}).get("strict_mode", False)
        # If not explicit, derive from urgency/history
        if state.get("context", {}).get("urgency") == "HIGH":
            strict_mode = True
        adaptive_decision = AdaptiveDecision(
            strictMode=strict_mode
        )
        
        # 6. Checkout Decision
        prevention_data = state.get("prevention_data", {})
        allow_checkout = prevention_data.get("allow_checkout", True)
        
        blocking_issues = []
        if not allow_checkout:
            blocking_issues.append(prevention_data.get("reason", "Checkout blocked by prevention agent."))
            
        checkout_res = CheckoutDecision(
            allowCheckout=allow_checkout,
            blockingIssues=blocking_issues
        )
        
        # 7. Recommendations
        recs = []
        for rec in state.get("recommendations_data", []):
            recs.append(RecommendationItem(
                productId=rec.get("product_id"),
                name=rec.get("name", "Product Substitute"),
                price=float(rec.get("price", 0.0)),
                reason=rec.get("reason", "Highly recommended substitute")
            ))
            
        return MissionExecutionResponse(
            mission=mission_info,
            verification=verification_res,
            risk=risk_res,
            simulation=simulation_res,
            adaptiveDecision=adaptive_decision,
            checkout=checkout_res,
            recommendations=recs
        )

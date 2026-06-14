from typing import Dict, Any, List
from orchestration.agents.orchestrator.schemas import (
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
        
        # 2. Verification (V2 enriched)
        verification_data = state.get("verification_data", {})
        verification_res = VerificationResult(
            score=verification_data.get("verification_score", 0),
            missingItems=verification_data.get("missing_items", []),
            criticalCompletion=verification_data.get("critical_completion", 0.0),
            importantCompletion=verification_data.get("important_completion", 0.0),
            optionalCompletion=verification_data.get("optional_completion", 0.0),
            criticalMissing=verification_data.get("critical_missing", []),
            importantMissing=verification_data.get("important_missing", []),
            optionalMissing=verification_data.get("optional_missing", []),
            recommendedProducts=verification_data.get("recommended_products", []),
        )
        
        # 3. Risk (V2 multi-dimensional)
        risk_data = state.get("risk_data", {})
        risk_score = risk_data.get("risk_score", 0)
        overall_risk_label = "LOW"
        if risk_score >= 70:
            overall_risk_label = "HIGH"
        elif risk_score >= 30:
            overall_risk_label = "MEDIUM"
            
        risk_res = RiskResult(
            overallRisk=overall_risk_label,
            completionRisk=risk_data.get("completion_risk", 0),
            quantityRisk=risk_data.get("quantity_risk", 0),
            compatibilityRisk=risk_data.get("compatibility_risk", 0),
            budgetRisk=risk_data.get("budget_risk", 0),
            timingRisk=risk_data.get("timing_risk", 0),
        )
        
        # 4. Simulation (V2 graph-driven)
        simulation_data = state.get("simulation_data", {})
        success_probability = simulation_data.get("success_probability", 0)
        # Handle legacy format
        if isinstance(success_probability, float) and success_probability <= 1.0:
            success_probability = int(success_probability * 100)
        sim_details = simulation_data.get("details", {})
        if not success_probability and sim_details:
            success_probability = int(sim_details.get("predicted_satisfaction", 0.5) * 100)
            
        simulation_res = SimulationResult(
            successProbability=int(success_probability),
            requiredProducts=simulation_data.get("required_products", {}),
            availableProducts=simulation_data.get("available_products", {}),
            quantityGaps=simulation_data.get("quantity_gaps", {}),
            assumptions=simulation_data.get("assumptions", []),
        )
        
        # 5. Adaptive Decision (V2 persona)
        adaptive_data = state.get("adaptive_data", {})
        strict_mode = adaptive_data.get("adapted_rules", {}).get("strict_mode", False)
        if state.get("context", {}).get("urgency") == "HIGH":
            strict_mode = True
        adaptive_decision = AdaptiveDecision(
            strictMode=strict_mode,
            shopperType=adaptive_data.get("shopper_type", ""),
            recommendedIntervention=adaptive_data.get("recommended_intervention", ""),
        )
        
        # 6. Checkout Decision (V2 explainable)
        prevention_data = state.get("prevention_data", {})
        allow_checkout = prevention_data.get("allow_checkout", True)
        
        blocking_issues = []
        if not allow_checkout:
            blocking_issues.append(prevention_data.get("reason", "Checkout blocked by prevention agent."))
        
        # Build explainable reason
        mission_name = mission_data.get("name", state.get("missionId", "Mission"))
        readiness = verification_data.get("verification_score", 0)
        critical_missing = verification_data.get("critical_missing", [])
        important_missing = verification_data.get("important_missing", [])
        
        if allow_checkout:
            reason = f"{mission_name} mission is {readiness}% ready. All critical items present."
        else:
            missing_desc = ""
            if critical_missing:
                missing_desc = f" Missing critical item{'s' if len(critical_missing) > 1 else ''}: {', '.join(c.replace('_', ' ').title() for c in critical_missing)}."
            elif important_missing:
                missing_desc = f" Missing important item{'s' if len(important_missing) > 1 else ''}: {', '.join(c.replace('_', ' ').title() for c in important_missing)}."
            reason = f"{mission_name} mission is only {readiness}% ready.{missing_desc}"
        
        # Recommended actions
        recommended_actions = []
        for item in critical_missing:
            recommended_actions.append(f"Add {item.replace('_', ' ').title()}")
        for item in important_missing:
            recommended_actions.append(f"Add {item.replace('_', ' ').title()}")
        
        # Risk summary
        risk_summary = {
            "completion_risk": risk_data.get("completion_risk", 0),
            "quantity_risk": risk_data.get("quantity_risk", 0),
            "compatibility_risk": risk_data.get("compatibility_risk", 0),
            "timing_risk": risk_data.get("timing_risk", 0),
            "budget_risk": risk_data.get("budget_risk", 0),
        }
        
        checkout_res = CheckoutDecision(
            allowCheckout=allow_checkout,
            blockingIssues=blocking_issues,
            reason=reason,
            recommendedActions=recommended_actions,
            riskSummary=risk_summary,
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

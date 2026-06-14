from typing import List
from engines.domains.risk.schemas import RiskRequest, RiskResponseData, RiskRisk
from foundation.graph.repository import GraphRepository

class RiskService:
    def __init__(self):
        self.graph_repo = GraphRepository()

    def analyze(self, data: RiskRequest) -> RiskResponseData:
        risks = []
        
        # Calculate key metrics
        critical_missing_count = len(data.critical_missing)
        
        # Calculate dependency missing count
        dependency_missing_count = 0
        for item in data.cart_products:
            deps = self.graph_repo.query_by_pk(f"PRODUCT#{item}", "DEPENDS_ON#")
            for dep in deps:
                target = dep.get("SK", "").split("#")[-1]
                if target and target not in data.cart_products:
                    dependency_missing_count += 1
                    
        # Check substitutions coverage
        no_subs_count = 0
        for missing in data.critical_missing:
            subs = self.graph_repo.query_by_pk(f"PRODUCT#{missing}", "SUBSTITUTES_FOR#")
            if not subs:
                no_subs_count += 1
                
        # 1. Check for Missing Critical Items
        if critical_missing_count > 0:
            severity = "HIGH" if critical_missing_count > 2 else "MEDIUM"
            risks.append(RiskRisk(
                type="MISSING_CRITICAL_ITEM",
                severity=severity,
                reason=f"Missing {critical_missing_count} critical items required for the mission."
            ))
            
        # 2. Check for Low Readiness
        if data.readiness_score < 60:
            severity = "HIGH" if data.readiness_score < 40 else "MEDIUM"
            risks.append(RiskRisk(
                type="INSUFFICIENT_QUANTITY",
                severity=severity,
                reason=f"Cart readiness is low ({data.readiness_score}%), indicating insufficient mission coverage."
            ))
            
        # 3. Budget Overrun
        if data.budget and data.total_cost > data.budget:
            overrun = data.total_cost - data.budget
            risks.append(RiskRisk(
                type="BUDGET_OVERRUN",
                severity="HIGH",
                reason=f"Estimated cost exceeds budget of {data.budget} by {overrun:.2f}."
            ))
            
        # 4. Low Substitution Coverage
        if no_subs_count > 0:
            risks.append(RiskRisk(
                type="LOW_SUBSTITUTION_COVERAGE",
                severity="MEDIUM",
                reason=f"{no_subs_count} missing critical items have no known substitutes in the graph."
            ))
            
        # 5. Missing Dependencies
        if dependency_missing_count > 0:
            severity = "HIGH" if dependency_missing_count > 1 else "MEDIUM"
            risks.append(RiskRisk(
                type="MISSION_DEPENDENCY_MISSING",
                severity=severity,
                reason=f"{dependency_missing_count} dependent accessory items are missing from the cart."
            ))

        # Base risk derived from 100 - readiness
        base_risk = 100 - data.readiness_score
        
        # Calculate calibrated risk score
        risk_score = (base_risk * 0.4) + (critical_missing_count * 8) + (dependency_missing_count * 6) + (no_subs_count * 2)
        
        # Apply budget overrun penalty
        if data.budget and data.total_cost > data.budget:
            risk_score += 15
            
        # Cap risk score
        risk_score = int(min(100, max(0, risk_score)))
        
        # Determine risk level range
        if risk_score <= 25:
            risk_level = "LOW"
        elif risk_score <= 50:
            risk_level = "MEDIUM"
        elif risk_score <= 75:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
            
        return RiskResponseData(
            risk_score=risk_score,
            risk_level=risk_level,
            risks=risks
        )

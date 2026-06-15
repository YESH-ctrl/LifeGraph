import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class ConsistencyValidator:
    def __init__(self):
        pass

    def validate_consistency(
        self,
        items_count: int,
        final_action: str,
        risk_level: str,
        risk_score: int,
        critical_missing_count: int,
        readiness_score: int,
        optimized_success: int
    ) -> Tuple[bool, List[str], int]:
        """
        Validates score and status relationships.
        Returns: (is_consistent, issues_list, consistency_score)
        """
        issues = []
        consistency_score = 100

        # Rule 1: Cannot Proceed to Checkout if cart is empty
        if items_count == 0 and final_action == "Proceed to Checkout":
            issues.append("Contradiction: Cart is empty (items_count=0) but final action is 'Proceed to Checkout'. Status must be Review Cart.")
            consistency_score -= 35

        # Rule 2: Risk cannot be LOW if there are large critical missing items
        if risk_level == "LOW" and critical_missing_count >= 10:
            issues.append(f"Contradiction: Risk level is LOW (score: {risk_score}) but critical missing count is high ({critical_missing_count}).")
            consistency_score -= 30

        # Rule 3: Success probability cannot be high if readiness is very low
        if optimized_success >= 90 and readiness_score <= 30:
            issues.append(f"Contradiction: Optimized success probability is high ({optimized_success}%) but readiness is extremely low ({readiness_score}%).")
            consistency_score -= 35

        # Rule 4: Readiness score cannot be 100% if critical missing count is greater than 0
        if readiness_score == 100 and critical_missing_count > 0:
            issues.append(f"Contradiction: Readiness score is 100% but there are {critical_missing_count} critical missing items.")
            consistency_score -= 25

        # Rule 5: Critical risk cannot coexist with high success probability
        if risk_level == "CRITICAL" and optimized_success >= 85:
            issues.append(f"Contradiction: Risk level is CRITICAL but success probability is high ({optimized_success}%).")
            consistency_score -= 20

        # Rule 6: Success probability must be greater than or equal to current success (readiness score)
        current_success = min(95, max(0, readiness_score))
        if optimized_success < current_success:
            issues.append(f"Contradiction: Optimized success probability ({optimized_success}%) is lower than baseline readiness-derived success ({current_success}%).")
            consistency_score -= 20

        # Cap score
        consistency_score = max(0, min(100, consistency_score))
        is_consistent = len(issues) == 0

        return is_consistent, issues, consistency_score

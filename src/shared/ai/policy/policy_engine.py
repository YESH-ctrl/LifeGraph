import os
import logging
from typing import Dict, Any, List, Tuple
from .policy_rules import RULES, is_uuid_like
from shared.ai.grounding.grounding_engine import GroundingEngine

logger = logging.getLogger(__name__)

# --- CERTIFICATION THRESHOLDS (Task 2 - Phase 7.1) ---
TRUSTED_THRESHOLDS = {
    "grounding_score": 95,
    "catalog_validity_score": 100,
    "graph_validity_score": 100,
    "reality_score": 85,
    "consistency_score": 95,
    "decision_override_rate": 0.20,
}

class PolicyEngine:
    def __init__(self):
        self.grounding = GroundingEngine()

    def evaluate_and_repair(self, state: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Runs the validation rules, applies repairs, and generates the certification response.
        Returns: (final_state, certification_payload)
        """
        repair_log = []
        violations_count = 0
        hard_failures = []

        # 1. Catalog and Graph Hard Validation (Task 9 & 10)
        # Check if recommended additions contain hallucinated/missing catalog products
        if "verification" in state:
            recs = state["verification"].get("recommended_products", [])
            valid_recs = []
            for r in recs:
                if not r:
                    continue
                exists, _, _ = self.grounding.validate_product_in_catalog(r)
                if exists:
                    valid_recs.append(r)
                else:
                    violations_count += 1
                    repair_log.append({
                        "rule": "RULE_CATALOG_VIOLATION",
                        "field": "verification.recommended_products",
                        "old_value": r,
                        "new_value": None
                    })
            state["verification"]["recommended_products"] = valid_recs

        # --- TASK 1 (Phase 7.1): Live Execution Enforcement ---
        ai_runtime = state.get("ai_runtime") or {}
        ai_metadata = state.get("ai_metadata") or {}
        provider = ai_runtime.get("provider") or ai_metadata.get("provider")
        mode_env = os.environ.get("MODE", "BEDROCK_LIVE")

        if mode_env == "BEDROCK_LIVE" and provider == "simulation":
            hard_failures.append("BLOCKED: Simulation provider detected in BEDROCK_LIVE mode. All responses must use Bedrock inference.")
            # Immediately return FAILED certification
            return {
                "status": "BLOCKED",
                "error": "Live Execution Violation",
                "failures": hard_failures,
                "certification": {
                    "status": "FAILED",
                    "policy_score": 0,
                    "repaired": False,
                    "trust_level": "FAILED",
                    "errors": hard_failures
                },
                "ai_runtime": ai_runtime,
                "ai_metadata": ai_metadata,
                "trust_level": "FAILED",
                "policy_score": 0,
                "repair_log": []
            }, {
                "status": "FAILED",
                "policy_score": 0,
                "repaired": False,
                "trust_level": "FAILED",
                "errors": hard_failures
            }

        # Check for grounding failures: changes accepted but lacking graph verification
        # If audit score is 0 or metadata is corrupted, treat as hard failure
        if not ai_metadata and not ai_runtime:
            hard_failures.append("Corrupted metadata: Missing ai_metadata structure.")

        # 2. Run Policy Rule Registry
        for rule in RULES:
            try:
                if rule.validate(state):
                    violations_count += 1
                    logger.warning(f"Policy violation detected: {rule.id} - {rule.description}")
                    
                    # Apply Repair
                    state, rule_logs = rule.repair(state)
                    repair_log.extend(rule_logs)
            except Exception as e:
                logger.error(f"Error executing policy rule {rule.id}: {e}")
                hard_failures.append(f"Rule execution error on {rule.id}: {str(e)}")

        # 3. Handle Hard Failures (Task 9)
        # If any raw UUID leak is unrepairable or graph references are completely broken:
        for leak in state.get("reasoning", []):
            if is_uuid_like(leak) and "[CLEANED]" not in leak:
                # Critical block check
                hard_failures.append(f"Hard Failure: Unsanitized raw UUID leak in reasoning: {leak}")

        if hard_failures:
            logger.error(f"Critical policy violations blocked the response: {hard_failures}")
            return {
                "status": "BLOCKED",
                "error": "Hard Policy Violation",
                "failures": hard_failures,
                "certification": {
                    "status": "FAILED",
                    "policy_score": 0,
                    "repaired": False,
                    "errors": hard_failures
                }
            }, {
                "status": "FAILED",
                "policy_score": 0,
                "repaired": False,
                "errors": hard_failures
            }

        # 4. Construct Response Certification & Trust Level (Task 5 & 7)
        repaired = len(repair_log) > 0
        policy_score = max(0, 100 - (len(repair_log) * 15))

        # --- TASK 2 (Phase 7.1): Certification Reconciliation ---
        # TRUSTED requires ALL score thresholds to be met
        grounding_score = state.get("grounding_score", 0)
        catalog_validity_score = state.get("catalog_validity_score", 0)
        graph_validity_score = state.get("graph_validity_score", 0)
        reality_score = state.get("reality_score", 0)
        consistency_score = state.get("consistency_score", 0)

        metrics = state.get("ai_metadata", {}).get("metrics", {}) or {}
        decision_override_rate = metrics.get("decision_override_rate", 0.0)

        runtime_truth = state.get("runtime_truth")
        if runtime_truth is None:
            provider_matches = True
            no_fallback_used = True
        else:
            provider_matches = runtime_truth.get("provider_matches_runtime") is True
            no_fallback_used = runtime_truth.get("fallback_used") is False

        trust_conditions = {
            "grounding_score": grounding_score >= TRUSTED_THRESHOLDS["grounding_score"],
            "catalog_validity_score": catalog_validity_score >= TRUSTED_THRESHOLDS["catalog_validity_score"],
            "graph_validity_score": graph_validity_score >= TRUSTED_THRESHOLDS["graph_validity_score"],
            "reality_score": reality_score >= TRUSTED_THRESHOLDS["reality_score"],
            "consistency_score": consistency_score >= TRUSTED_THRESHOLDS["consistency_score"],
            "decision_override_rate": decision_override_rate <= TRUSTED_THRESHOLDS["decision_override_rate"],
            "provider_matches_runtime": provider_matches,
            "fallback_used": no_fallback_used,
        }

        all_trust_conditions_met = all(trust_conditions.values())
        failed_conditions = [k for k, v in trust_conditions.items() if not v]

        if repaired:
            trust_level = "AUTO_REPAIRED"
        elif violations_count > 0:
            trust_level = "WARNING"
        elif all_trust_conditions_met:
            trust_level = "TRUSTED"
        else:
            trust_level = "WARNING"
            logger.warning(f"TRUSTED certification denied. Failed conditions: {failed_conditions}")

        cert_status = trust_level  # Use trust_level directly to remove CERTIFIED

        certification = {
            "status": cert_status,
            "policy_score": policy_score,
            "repaired": repaired,
            "trust_level": trust_level,
            "repair_log": repair_log,
            "trust_conditions": trust_conditions
        }

        # 5. Compute Self-Healing Metrics (Task 8)
        # These are added directly to state metrics
        metrics = ai_metadata.get("metrics", {})
        
        metrics["repair_rate"] = 1.0 if repaired else 0.0
        metrics["policy_violation_rate"] = 1.0 if violations_count > 0 else 0.0
        metrics["certification_rate"] = 1.0 if cert_status == "CERTIFIED" else 0.0
        metrics["trust_score"] = int(policy_score)
        metrics["mean_repairs_per_request"] = float(len(repair_log))

        # Inject into output response
        state["certification"] = certification
        state["repair_log"] = repair_log
        state["trust_level"] = trust_level

        # Also place at top level for easy consumer access
        state["policy_score"] = policy_score

        return state, certification

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class EvaluationEngine:
    def __init__(self):
        pass

    def evaluate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the orchestrator final response state.
        Scores decision, reasoning, grounding, and user outcome quality.
        Returns a dictionary containing the evaluation scores and agent scorecards.
        """
        ai_metadata = state.get("ai_metadata", {})
        metrics = ai_metadata.get("metrics", {})
        
        # 1. Grounding Quality Score
        grounding_score = state.get("grounding_score", metrics.get("grounding_score", 100))
        
        # 2. Decision Quality Score
        # Heavily penalizes policy violations and rewards consistency
        consistency_score = state.get("consistency_score", metrics.get("consistency_score", 100))
        repair_log = state.get("repair_log", [])
        policy_violations_count = len(repair_log)
        
        decision_score = max(0, int(consistency_score * 0.7 + (100 - (policy_violations_count * 20)) * 0.3))
        
        # 3. Reasoning Quality Score
        reasoning_list = state.get("reasoning", [])
        reasoning_score = 100
        if not reasoning_list:
            reasoning_score = 0
        else:
            # Penalize very short reasoning lists
            if len(reasoning_list) < 3:
                reasoning_score -= 20
            # Penalize generic/placeholder text
            placeholders = ["placeholder", "todo", "unknown", "example item"]
            for r in reasoning_list:
                r_lower = r.lower()
                if any(p in r_lower for p in placeholders):
                    reasoning_score -= 15
                if len(r) < 15:  # Too short explanation
                    reasoning_score -= 5
            reasoning_score = max(0, reasoning_score)

        # 4. User Outcome Quality Score
        # Combines coherence with optimized success score
        cart = state.get("cart", {})
        coherence = cart.get("mission_coherence_score", state.get("mission_coherence_score", 100))
        simulation = state.get("simulation", {})
        opt_success = simulation.get("optimized_success", 0)
        
        outcome_score = int(coherence * 0.4 + opt_success * 0.6)

        # 5. Combined evaluation_score
        evaluation_score = int(
            0.3 * grounding_score +
            0.3 * decision_score +
            0.2 * reasoning_score +
            0.2 * outcome_score
        )

        # 6. Generate Agent Scorecards
        scorecards = self._generate_scorecards(state, evaluation_score)

        # Compute efficiency metrics
        cost_usd = ai_metadata.get("execution_cost_usd", 0.0)
        latency_sec = ai_metadata.get("latency_sec", 0.0)
        
        quality_per_dollar = round(evaluation_score / cost_usd, 2) if cost_usd > 0 else 0.0
        quality_per_second = round(evaluation_score / latency_sec, 2) if latency_sec > 0 else 0.0

        eval_result = {
            "evaluation_score": evaluation_score,
            "grounding_score": grounding_score,
            "decision_score": decision_score,
            "reasoning_score": reasoning_score,
            "outcome_score": outcome_score,
            "scorecards": scorecards,
            "quality_per_dollar": quality_per_dollar,
            "quality_per_second": quality_per_second
        }

        # Inject back into state metadata
        if "ai_metadata" in state:
            state["ai_metadata"]["evaluation"] = eval_result
        state["evaluation_score"] = evaluation_score

        return eval_result

    def _generate_scorecards(self, state: Dict[str, Any], overall_eval_score: int) -> Dict[str, Any]:
        """
        Computes scorecards for the 7 agents:
        Mission, Cart, Verification, Risk, Regret, Simulation, Auditor.
        """
        ai_metadata = state.get("ai_metadata", {})
        auditor_report = ai_metadata.get("auditor_report", {})
        auditor_analysis = auditor_report.get("ai_analysis", {})
        auditor_failures = auditor_analysis.get("failures", [])
        
        repair_log = state.get("repair_log", [])
        
        agents = ["mission", "cart", "verification", "risk", "regret", "simulation", "auditor"]
        scorecards = {}

        for agent in agents:
            # Base stats
            accuracy = 100
            override_effectiveness = 100
            grounding_compliance = 100
            violations = 0
            repairs = 0
            predicted_confidence = 1.0

            # Map agent analysis data from metadata
            agent_analysis_key = f"{agent}_analysis"
            agent_data = ai_metadata.get(agent_analysis_key, {})
            if not agent_data and agent == "auditor":
                agent_data = auditor_report
            
            if agent_data:
                predicted_confidence = agent_data.get("confidence", 1.0)

            # Count repairs targeting this agent's domain
            # We map fields in repair_log to specific agents
            agent_repair_fields = {
                "mission": ["mission"],
                "cart": ["cart"],
                "verification": ["verification", "readiness"],
                "risk": ["risk"],
                "regret": ["regret_prevention", "forgotten"],
                "simulation": ["simulation"],
                "auditor": ["auditor"]
            }

            for rep in repair_log:
                rule_id = rep.get("rule", "")
                field = rep.get("field", "")
                
                # Match by field or rule ID prefix
                is_match = False
                for f in agent_repair_fields[agent]:
                    if f in field.lower() or f in rule_id.lower():
                        is_match = True
                        break
                
                if is_match:
                    repairs += 1
                    violations += 1

            # Accuracy drops if there are agent-specific failures detected by the auditor or policy engine
            if repairs > 0:
                accuracy = max(0, 100 - (repairs * 25))
            
            # Grounding compliance
            if agent == "auditor":
                grounding_compliance = ai_metadata.get("metrics", {}).get("grounding_score", 100)
            else:
                accepted_changes = agent_data.get("accepted_changes", [])
                rejected_changes = agent_data.get("rejected_changes", [])
                total_changes = len(accepted_changes) + len(rejected_changes)
                if total_changes > 0:
                    grounding_compliance = int((len(accepted_changes) / total_changes) * 100)
                else:
                    grounding_compliance = 100

            # Override effectiveness: are the suggested changes accepted and not repaired/rejected?
            # If agent suggests overrides but they trigger repairs or rejections, effectiveness is lowered.
            suggested_changes = agent_data.get("recommended_changes", [])
            if suggested_changes:
                rejected_count = len(agent_data.get("rejected_changes", []))
                effective_count = len(suggested_changes) - rejected_count - repairs
                override_effectiveness = max(0, int((effective_count / len(suggested_changes)) * 100))
            else:
                override_effectiveness = 100

            # Confidence Calibration
            # Predicted Confidence (0.0 to 1.0) scaled to 100 vs actual quality (average of accuracy, effectiveness, grounding)
            actual_quality = (accuracy + override_effectiveness + grounding_compliance) / 3.0
            confidence_pct = predicted_confidence * 100
            # Calibration error is absolute difference
            calibration_error = abs(confidence_pct - actual_quality)
            confidence_calibration = max(0, int(100 - calibration_error))

            scorecards[agent] = {
                "accuracy": accuracy,
                "override_effectiveness": override_effectiveness,
                "grounding_compliance": grounding_compliance,
                "policy_violations": violations,
                "repair_frequency": repairs,
                "confidence_calibration": confidence_calibration
            }

        return scorecards

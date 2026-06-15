import json
import os
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ReplayEngine:
    def __init__(self, history_file: str = "decision_history.json"):
        self.history_file = history_file

    def save_decision(self, record: Dict[str, Any]):
        """
        Saves a decision log record to the history file.
        Contains query, mission, cart, verification, risk, simulation, auditor, certification.
        """
        history = self.load_history()
        
        # Prune large outputs or simplify to save space if needed, but ensure we keep essential fields
        history.append({
            "timestamp": time.time(),
            "query": record.get("query", ""),
            "mission": record.get("mission", {}),
            "cart": record.get("cart", {}),
            "verification": record.get("verification", {}),
            "risk": record.get("risk", {}),
            "simulation": record.get("simulation", {}),
            "reasoning": record.get("reasoning", []),
            "ai_metadata": record.get("ai_metadata", {}),
            "certification": record.get("certification", {}),
            "repair_log": record.get("repair_log", []),
            "trust_level": record.get("trust_level", "TRUSTED"),
            "evaluation": record.get("ai_metadata", {}).get("evaluation", {}),
            "policy_score": record.get("policy_score", 100)
        })

        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write decision history: {e}")

    def load_history(self) -> List[Dict[str, Any]]:
        """
        Loads the decision history dataset from the file.
        """
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            logger.error(f"Failed to read decision history: {e}")
            return []

    def replay_runs(self, orchestrator, limit: int = 5) -> Dict[str, Any]:
        """
        Replays historical requests through the orchestrator.
        Compares original runs with replayed runs.
        """
        history = self.load_history()
        if not history:
            return {
                "total_replayed": 0,
                "msg": "No historical runs found in history database."
            }

        records_to_replay = history[-limit:]
        comparisons = []
        
        total_quality_delta = 0.0
        total_cost_delta = 0.0
        total_latency_delta = 0.0
        risk_reduction_count = 0

        for idx, orig in enumerate(records_to_replay):
            query = orig.get("query", "")
            if not query:
                continue
            
            logger.info(f"Replaying query {idx+1}: '{query}'...")
            t0 = time.time()
            new_res = orchestrator.run_outcome_intelligence(query)
            latency = time.time() - t0

            # Compile comparison metrics
            orig_eval = orig.get("evaluation", {})
            orig_score = orig_eval.get("evaluation_score", orig.get("policy_score", 100))
            orig_cost = orig.get("ai_metadata", {}).get("execution_cost_usd", 0.0)

            new_eval = new_res.get("ai_metadata", {}).get("evaluation", {})
            new_score = new_eval.get("evaluation_score", new_res.get("policy_score", 100))
            new_cost = new_res.get("ai_metadata", {}).get("execution_cost_usd", 0.0)

            quality_delta = new_score - orig_score
            cost_delta = new_cost - orig_cost
            
            # Estimate original latency if not saved (default to average 1.5s if missing)
            orig_latency = orig.get("ai_metadata", {}).get("latency_sec", 1.5)
            latency_delta = latency - orig_latency

            # Check if risk decreased (LOW risk is better than HIGH risk)
            risk_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            orig_risk = risk_levels.get(orig.get("risk", {}).get("risk_level", "LOW"), 1)
            new_risk = risk_levels.get(new_res.get("risk", {}).get("risk_level", "LOW"), 1)
            if new_risk < orig_risk:
                risk_reduction_count += 1

            total_quality_delta += quality_delta
            total_cost_delta += cost_delta
            total_latency_delta += latency_delta

            comparisons.append({
                "query": query,
                "original": {
                    "evaluation_score": orig_score,
                    "cost_usd": orig_cost,
                    "trust_level": orig.get("trust_level", "TRUSTED"),
                    "risk_level": orig.get("risk", {}).get("risk_level", "LOW")
                },
                "replayed": {
                    "evaluation_score": new_score,
                    "cost_usd": new_cost,
                    "trust_level": new_res.get("trust_level", "TRUSTED"),
                    "risk_level": new_res.get("risk", {}).get("risk_level", "LOW")
                },
                "delta": {
                    "quality_score": quality_delta,
                    "cost_usd": cost_delta,
                    "latency_sec": latency_delta
                }
            })

        count = len(comparisons)
        if count == 0:
            return {"total_replayed": 0}

        return {
            "total_replayed": count,
            "comparisons": comparisons,
            "averages": {
                "quality_improvement_score": round(total_quality_delta / count, 2),
                "cost_savings_usd": round(-total_cost_delta / count, 6),
                "latency_difference_sec": round(total_latency_delta / count, 3)
            },
            "risk_mitigations_triggered": risk_reduction_count
        }

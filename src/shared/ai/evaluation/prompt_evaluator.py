import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class PromptEvaluator:
    def __init__(self):
        # Stores stats: { prompt_name: { version: { "runs": 0, "total_cost": 0.0, "total_latency": 0.0, "total_quality": 0.0, "hallucinations": 0 } } }
        self.stats: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def record_run(
        self,
        prompt_name: str,
        version: str,
        cost: float,
        latency: float,
        decision_quality: float,
        is_hallucination: bool,
        evaluation_score: float
    ):
        """
        Records statistics for a specific prompt run.
        """
        if prompt_name not in self.stats:
            self.stats[prompt_name] = {}
        if version not in self.stats[prompt_name]:
            self.stats[prompt_name][version] = {
                "runs": 0,
                "total_cost": 0.0,
                "total_latency": 0.0,
                "total_quality": 0.0,
                "total_evaluation_score": 0.0,
                "hallucinations": 0
            }

        entry = self.stats[prompt_name][version]
        entry["runs"] += 1
        entry["total_cost"] += cost
        entry["total_latency"] += latency
        entry["total_quality"] += decision_quality
        entry["total_evaluation_score"] += evaluation_score
        if is_hallucination:
            entry["hallucinations"] += 1

    def get_leaderboard(self, sort_by: str = "efficiency_ratio") -> List[Dict[str, Any]]:
        """
        Generates the Prompt Leaderboard, ranking prompt configurations.
        sort_by options: 'efficiency_ratio' (quality/cost), 'quality', 'cost', 'latency'
        """
        leaderboard = []
        for prompt_name, versions in self.stats.items():
            for version, data in versions.items():
                runs = data["runs"]
                if runs == 0:
                    continue
                
                avg_cost = data["total_cost"] / runs
                avg_latency = data["total_latency"] / runs
                avg_quality = data["total_quality"] / runs
                avg_eval = data["total_evaluation_score"] / runs
                hallucination_rate = data["hallucinations"] / runs

                # Calculate quality-to-cost ratio (higher is better)
                # Safeguard against zero cost
                cost_factor = avg_cost if avg_cost > 0 else 0.00001
                efficiency_ratio = avg_eval / cost_factor

                leaderboard.append({
                    "prompt_name": prompt_name,
                    "version": version,
                    "runs": runs,
                    "avg_cost_usd": round(avg_cost, 6),
                    "avg_latency_sec": round(avg_latency, 3),
                    "avg_decision_quality": round(avg_quality, 1),
                    "avg_evaluation_score": round(avg_eval, 1),
                    "hallucination_rate": round(hallucination_rate, 3),
                    "efficiency_ratio": round(efficiency_ratio, 2)
                })

        # Sorting
        if sort_by == "cost":
            leaderboard.sort(key=lambda x: x["avg_cost_usd"])
        elif sort_by == "latency":
            leaderboard.sort(key=lambda x: x["avg_latency_sec"])
        elif sort_by == "quality":
            leaderboard.sort(key=lambda x: x["avg_evaluation_score"], reverse=True)
        else:
            # Sort by quality/cost ratio
            leaderboard.sort(key=lambda x: x["efficiency_ratio"], reverse=True)

        return leaderboard

    def ab_test_compare(
        self,
        runs_a: List[Dict[str, Any]],
        runs_b: List[Dict[str, Any]],
        runs_c: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Compares results from Prompt/Variant A vs B vs C side-by-side.
        Each list of runs contains dictionaries with:
        optimized_success, repair_rate, trust_score, audit_score, grounding_score, latency, cost.
        """
        def compile_metrics(runs: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
            if not runs:
                return {
                    "variant": name,
                    "runs": 0,
                    "avg_success": 0.0,
                    "repair_rate": 0.0,
                    "avg_trust_score": 0.0,
                    "avg_audit_score": 0.0,
                    "avg_grounding_score": 0.0,
                    "avg_latency": 0.0,
                    "avg_cost": 0.0
                }
            count = len(runs)
            avg_success = sum(r.get("optimized_success", 0) for r in runs) / count
            repair_rate = sum(1 for r in runs if r.get("repaired", False) or r.get("repair_rate", 0.0) > 0) / count
            avg_trust = sum(r.get("trust_score", r.get("policy_score", 100)) for r in runs) / count
            avg_audit = sum(r.get("audit_score", 100) for r in runs) / count
            avg_grounding = sum(r.get("grounding_score", 100) for r in runs) / count
            avg_latency = sum(r.get("latency", 0.0) for r in runs) / count
            avg_cost = sum(r.get("cost", 0.0) for r in runs) / count

            return {
                "variant": name,
                "runs": count,
                "avg_success": round(avg_success, 1),
                "repair_rate": round(repair_rate, 3),
                "avg_trust_score": round(avg_trust, 1),
                "avg_audit_score": round(avg_audit, 1),
                "avg_grounding_score": round(avg_grounding, 1),
                "avg_latency": round(avg_latency, 3),
                "avg_cost": round(avg_cost, 6)
            }

        comparison = {
            "variant_A": compile_metrics(runs_a, "Variant A"),
            "variant_B": compile_metrics(runs_b, "Variant B")
        }

        if runs_c is not None:
            comparison["variant_C"] = compile_metrics(runs_c, "Variant C")

        # Determine winner based on trust_score and optimized_success
        score_a = comparison["variant_A"]["avg_trust_score"] * 0.5 + comparison["variant_A"]["avg_success"] * 0.5
        score_b = comparison["variant_B"]["avg_trust_score"] * 0.5 + comparison["variant_B"]["avg_success"] * 0.5
        
        winner = "Variant A" if score_a >= score_b else "Variant B"
        
        if runs_c is not None:
            score_c = comparison["variant_C"]["avg_trust_score"] * 0.5 + comparison["variant_C"]["avg_success"] * 0.5
            if score_c > max(score_a, score_b):
                winner = "Variant C"

        comparison["winner"] = winner
        return comparison

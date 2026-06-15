import logging
from typing import Dict, Any, List
from collections import Counter
from .prompt_evaluator import PromptEvaluator
from .replay_engine import ReplayEngine

logger = logging.getLogger(__name__)

class ContinuousOptimizer:
    def __init__(self, evaluator: PromptEvaluator, replay_engine: ReplayEngine):
        self.evaluator = evaluator
        self.replay = replay_engine

    def generate_failure_dashboard(self) -> Dict[str, Any]:
        """
        Analyzes the decision history dataset to compile failure analytics.
        Tracks common failures, repairs, expensive prompts, and low-trust runs.
        """
        history = self.replay.load_history()
        total_runs = len(history)
        if total_runs == 0:
            return {
                "total_runs": 0,
                "msg": "No records in history database to compute dashboard metrics."
            }

        repaired_runs = 0
        blocked_runs = 0
        trusted_runs = 0
        warning_runs = 0
        total_cost = 0.0
        
        repair_counter = Counter()
        violations_counter = Counter()
        prompt_cost_counter = Counter()
        prompt_runs_counter = Counter()
        
        low_trust_responses = []

        for record in history:
            trust = record.get("trust_level", "TRUSTED")
            policy_score = record.get("policy_score", 100)
            
            if trust == "REPAIRED":
                repaired_runs += 1
            elif trust == "FAILED" or record.get("status") == "BLOCKED":
                blocked_runs += 1
            elif trust == "WARNING":
                warning_runs += 1
            else:
                trusted_runs += 1

            # Tally costs
            cost = record.get("ai_metadata", {}).get("execution_cost_usd", 0.0)
            total_cost += cost

            # Repair logs
            repair_log = record.get("repair_log", [])
            for rep in repair_log:
                rule = rep.get("rule", "UNKNOWN_RULE")
                repair_counter[rule] += 1
                violations_counter[rule] += 1

            # Prompts analysis from ai_metadata
            for agent in ["mission", "cart", "verification", "risk", "regret", "simulation", "auditor"]:
                agent_key = f"{agent}_analysis"
                agent_data = record.get("ai_metadata", {}).get(agent_key, {})
                if agent_data:
                    # We estimate prompt cost share
                    # Sonnet/Haiku pricing logic approximation
                    model = record.get("ai_metadata", {}).get("model", "sonnet")
                    prompt_cost = cost / 7.0  # evenly distribute average share
                    prompt_cost_counter[agent] += prompt_cost
                    prompt_runs_counter[agent] += 1

            # Track lowest trust responses (policy score < 80)
            if policy_score < 80 or trust == "FAILED":
                low_trust_responses.append({
                    "query": record.get("query", ""),
                    "trust_level": trust,
                    "policy_score": policy_score,
                    "repairs": len(repair_log)
                })

        # Sort low trust list
        low_trust_responses.sort(key=lambda x: x["policy_score"])

        # Calculate average costs by prompt agent
        expensive_prompts = []
        for agent, total_c in prompt_cost_counter.items():
            runs = prompt_runs_counter[agent]
            avg_c = total_c / runs if runs > 0 else 0.0
            expensive_prompts.append({
                "agent_prompt": agent,
                "total_cost_usd": round(total_c, 5),
                "avg_cost_usd": round(avg_c, 6)
            })
        expensive_prompts.sort(key=lambda x: x["avg_cost_usd"], reverse=True)

        return {
            "total_runs": total_runs,
            "trusted_runs": trusted_runs,
            "repaired_runs": repaired_runs,
            "warning_runs": warning_runs,
            "blocked_runs": blocked_runs,
            "overall_repaired_rate": round(repaired_runs / total_runs, 3),
            "overall_failure_rate": round(blocked_runs / total_runs, 3),
            "total_cost_usd": round(total_cost, 4),
            "avg_cost_per_request": round(total_cost / total_runs, 6),
            "most_common_repairs": dict(repair_counter.most_common(5)),
            "most_common_violations": dict(violations_counter.most_common(5)),
            "expensive_prompts": expensive_prompts[:3],
            "lowest_trust_responses": low_trust_responses[:5]
        }

    def run_optimization_loop(self) -> Dict[str, Any]:
        """
        Continuous Optimization Loop:
        Observe -> Evaluate -> Learn -> Optimize -> Deploy.
        Generates action items for prompt, cost, and routing tuning.
        """
        dashboard = self.generate_failure_dashboard()
        leaderboard = self.evaluator.get_leaderboard()

        recommendations = []

        # 1. Evaluate repair frequencies to suggest Prompt Tuning
        common_repairs = dashboard.get("most_common_repairs", {})
        for rule, count in common_repairs.items():
            if count >= 1:
                if "RULE_EMPTY_CART" in rule:
                    recommendations.append({
                        "category": "Prompt Optimization",
                        "target": "Cart Intelligence Agent Prompt / Master Orchestrator",
                        "finding": f"Empty cart violations triggered {count} times.",
                        "action": "Adjust Cart Intelligence Prompt to include rules preventing zero critical items, or force blueprint fallback.",
                        "priority": "HIGH"
                    })
                elif "RULE_UUID_LEAK" in rule:
                    recommendations.append({
                        "category": "Prompt Optimization",
                        "target": "All Agent Prompts (Reasoning Format)",
                        "finding": f"UUID leakage occurred {count} times in reasoning lists.",
                        "action": "Ensure all agent prompts explicitly forbid printing database UUID format patterns in text reasoning output.",
                        "priority": "CRITICAL"
                    })
                else:
                    recommendations.append({
                        "category": "Prompt Optimization",
                        "target": f"{rule} associated Agent",
                        "finding": f"Rule {rule} violated {count} times.",
                        "action": "Tune agent temperature or rewrite constraints in system prompt.",
                        "priority": "MEDIUM"
                    })

        # 2. Analyze costs and suggest routing adjustments
        expensive = dashboard.get("expensive_prompts", [])
        if expensive:
            for p in expensive:
                # If an agent is expensive and has high trust / no violations, we can downgrade its model to save cost
                agent = p["agent_prompt"]
                # E.g. if verification or risk is routed to Sonnet but could be run on Haiku
                if agent in ["verification", "risk", "regret"] and p["avg_cost_usd"] > 0.005:
                    recommendations.append({
                        "category": "Cost Reduction",
                        "target": f"Model Router for '{agent}' Agent",
                        "finding": f"Agent '{agent}' averages {p['avg_cost_usd']}$ per request.",
                        "action": f"Re-route '{agent}' from Claude Sonnet to Claude Haiku. Quality risk is low, saves ~80% cost.",
                        "priority": "MEDIUM"
                    })

        # 3. Analyze leaderboards to suggest active deployment changes
        for item in leaderboard:
            if item["hallucination_rate"] > 0.1:
                recommendations.append({
                    "category": "Prompt Deployment",
                    "target": f"{item['prompt_name']} v{item['version']}",
                    "finding": f"Prompt version v{item['version']} has a hallucination rate of {item['hallucination_rate']*100}%.",
                    "action": "Rollback prompt to prior version or add catalog guard interceptor.",
                    "priority": "HIGH"
                })

        # If dashboard total runs is low, offer default suggestions
        if len(recommendations) == 0:
            recommendations.append({
                "category": "General",
                "target": "System Registry",
                "finding": "System operating smoothly with low violations.",
                "action": "Maintain active model caching and monitor latency variance.",
                "priority": "LOW"
            })

        return {
            "dashboard_summary": {
                "total_runs": dashboard.get("total_runs", 0),
                "repaired_runs": dashboard.get("repaired_runs", 0),
                "blocked_runs": dashboard.get("blocked_runs", 0),
                "trust_score_avg": round(100 - (dashboard.get("overall_repaired_rate", 0.0) * 15), 1)
            },
            "recommendations": recommendations
        }

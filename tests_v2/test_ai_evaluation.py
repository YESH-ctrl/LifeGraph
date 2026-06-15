import pytest
import os
os.environ["MODE"] = "LOCAL_SIMULATION"
import json
from shared.ai.evaluation.evaluation_engine import EvaluationEngine
from shared.ai.evaluation.prompt_evaluator import PromptEvaluator
from shared.ai.evaluation.replay_engine import ReplayEngine
from shared.ai.evaluation.optimization_loop import ContinuousOptimizer
from orchestration.master_orchestrator import OutcomeOrchestrator

def test_evaluation_engine_scoring():
    engine = EvaluationEngine()
    
    # Inconsistent state that was repaired
    state = {
        "cart": {
            "items_count": 0,
            "mission_coherence_score": 90
        },
        "verification": {
            "readiness_score": 0,
            "critical_missing": []
        },
        "risk": {
            "risk_level": "HIGH",
            "risk_score": 100
        },
        "simulation": {
            "optimized_success": 0,
            "current_success": 0,
            "improvement": 0
        },
        "final_recommendation": {
            "action": "Review Cart"
        },
        "reasoning": [
            "Reason item 1 showing explanation details here.",
            "Reason item 2 showing explaining parameters.",
            "Reason item 3 showing additional explanations."
        ],
        "repair_log": [
            {"rule": "RULE_EMPTY_CART", "field": "verification.readiness_score", "old_value": 55, "new_value": 0}
        ],
        "ai_metadata": {
            "metrics": {
                "grounding_score": 80,
                "consistency_score": 75
            },
            "cart_analysis": {
                "confidence": 0.9,
                "recommended_changes": [{"type": "reject_product"}],
                "accepted_changes": [{"type": "reject_product"}],
                "rejected_changes": []
            }
        },
        "grounding_score": 80,
        "consistency_score": 75
    }

    eval_result = engine.evaluate(state)
    
    # Verify score presence
    assert "evaluation_score" in eval_result
    assert eval_result["evaluation_score"] >= 0
    assert eval_result["evaluation_score"] <= 100
    assert eval_result["grounding_score"] == 80
    assert eval_result["decision_score"] == int(75 * 0.7 + (100 - 20) * 0.3)
    assert eval_result["reasoning_score"] == 100  # 3 items, no placeholders
    assert eval_result["outcome_score"] == int(90 * 0.4 + 0 * 0.6)  # coherence 90, success 0
    
    # Verify scorecard presence
    assert "scorecards" in eval_result
    scorecards = eval_result["scorecards"]
    assert "mission" in scorecards
    assert "cart" in scorecards
    assert "verification" in scorecards
    assert "risk" in scorecards
    
    # Verify verification agent scorecard has repair count
    assert scorecards["verification"]["repair_frequency"] == 1
    assert scorecards["verification"]["policy_violations"] == 1
    assert scorecards["verification"]["accuracy"] < 100

def test_prompt_evaluator_leaderboard():
    evaluator = PromptEvaluator()
    
    # Record some runs
    evaluator.record_run("cart_agent", "1.0.0", cost=0.0050, latency=1.2, decision_quality=95.0, is_hallucination=False, evaluation_score=95.0)
    evaluator.record_run("cart_agent", "1.0.0", cost=0.0060, latency=1.4, decision_quality=85.0, is_hallucination=False, evaluation_score=85.0)
    
    evaluator.record_run("cart_agent", "1.1.0", cost=0.0030, latency=0.8, decision_quality=98.0, is_hallucination=False, evaluation_score=98.0)
    evaluator.record_run("cart_agent", "1.1.0", cost=0.0035, latency=0.9, decision_quality=96.0, is_hallucination=True, evaluation_score=96.0)

    leaderboard = evaluator.get_leaderboard(sort_by="efficiency_ratio")
    
    assert len(leaderboard) == 2
    # v1.1.0 should be first on efficiency ratio since it's much cheaper ($0.00325 vs $0.0055)
    assert leaderboard[0]["version"] == "1.1.0"
    assert leaderboard[0]["avg_latency_sec"] == 0.85
    assert leaderboard[0]["hallucination_rate"] == 0.5

def test_ab_testing_framework():
    evaluator = PromptEvaluator()
    
    runs_a = [
        {"optimized_success": 90, "repaired": False, "trust_score": 100, "latency": 1.1, "cost": 0.004},
        {"optimized_success": 85, "repaired": False, "trust_score": 100, "latency": 1.2, "cost": 0.004}
    ]
    runs_b = [
        {"optimized_success": 95, "repaired": True, "trust_score": 85, "latency": 1.6, "cost": 0.006},
        {"optimized_success": 90, "repaired": True, "trust_score": 85, "latency": 1.8, "cost": 0.006}
    ]
    
    comparison = evaluator.ab_test_compare(runs_a, runs_b)
    
    assert comparison["variant_A"]["avg_success"] == 87.5
    assert comparison["variant_B"]["avg_success"] == 92.5
    assert comparison["variant_A"]["repair_rate"] == 0.0
    assert comparison["variant_B"]["repair_rate"] == 1.0
    
    # Variant A should win because B has high repairs and low trust score (85)
    assert comparison["winner"] == "Variant A"

def test_replay_engine_and_history(tmp_path):
    test_db = os.path.join(tmp_path, "test_decision_history.json")
    replay = ReplayEngine(history_file=test_db)
    
    # Create mock record
    record = {
        "query": "Need rice, atta and oil for the month",
        "mission": {"detected_mission": "monthly_grocery_refill"},
        "cart": {"estimated_total_cost": 450, "items_count": 12},
        "verification": {"readiness_score": 90},
        "risk": {"risk_level": "LOW"},
        "simulation": {"optimized_success": 95},
        "ai_metadata": {
            "execution_cost_usd": 0.0042,
            "latency_sec": 1.2,
            "evaluation": {
                "evaluation_score": 92
            }
        },
        "certification": {"status": "CERTIFIED"},
        "repair_log": [],
        "trust_level": "TRUSTED",
        "policy_score": 100
    }
    
    # Save decision
    replay.save_decision(record)
    assert os.path.exists(test_db)
    
    # Load history
    history = replay.load_history()
    assert len(history) == 1
    assert history[0]["query"] == "Need rice, atta and oil for the month"
    
    # Test Replay runs
    orchestrator = OutcomeOrchestrator()
    replay_results = replay.replay_runs(orchestrator, limit=1)
    
    assert replay_results["total_replayed"] == 1
    assert "averages" in replay_results
    assert "quality_improvement_score" in replay_results["averages"]
    assert "cost_savings_usd" in replay_results["averages"]

def test_continuous_optimizer_loop(tmp_path):
    test_db = os.path.join(tmp_path, "test_decision_history.json")
    replay = ReplayEngine(history_file=test_db)
    evaluator = PromptEvaluator()
    
    # Populate history with some repairs/failures
    record_repaired = {
        "query": "Need rice for the month",
        "ai_metadata": {"execution_cost_usd": 0.0120}, # Expensive
        "repair_log": [
            {"rule": "RULE_UUID_LEAK", "field": "reasoning[0]", "old_value": "123e4567", "new_value": "[CLEANED]"}
        ],
        "trust_level": "REPAIRED",
        "policy_score": 85
    }
    record_trusted = {
        "query": "Healthy snacks",
        "ai_metadata": {"execution_cost_usd": 0.0020},
        "repair_log": [],
        "trust_level": "TRUSTED",
        "policy_score": 100
    }
    
    replay.save_decision(record_repaired)
    replay.save_decision(record_trusted)
    
    # Tally in evaluator
    evaluator.record_run("cart_agent", "1.0.0", cost=0.006, latency=1.2, decision_quality=85.0, is_hallucination=True, evaluation_score=85.0)
    
    optimizer = ContinuousOptimizer(evaluator, replay)
    dashboard = optimizer.generate_failure_dashboard()
    
    assert dashboard["total_runs"] == 2
    assert dashboard["repaired_runs"] == 1
    assert dashboard["trusted_runs"] == 1
    assert dashboard["most_common_repairs"]["RULE_UUID_LEAK"] == 1
    
    # Run loop to get recommendations
    loop_res = optimizer.run_optimization_loop()
    assert "recommendations" in loop_res
    recs = loop_res["recommendations"]
    assert len(recs) > 0
    # Must have a recommendation for UUID leak check because count is recorded
    assert any("UUID" in r["finding"] or "UUID" in r["action"] for r in recs)

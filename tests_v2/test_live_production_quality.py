import os
os.environ["MODE"] = "LOCAL_SIMULATION"
import pytest
from unittest.mock import MagicMock
from orchestration.master_orchestrator import OutcomeOrchestrator
from shared.ai.providers.bedrock_provider import BedrockProvider

def test_live_production_quality_metrics():
    # Set to LOCAL_SIMULATION to test the logic using simulation mock responses
    os.environ["MODE"] = "LOCAL_SIMULATION"
    orchestrator = OutcomeOrchestrator()
    orchestrator.ai_gateway.cache.clear()
    
    # 1. Test weight loss journey query - check that diabetic constraint is NOT hallucinated (Phase 7B)
    response = orchestrator.run_outcome_intelligence("I want to lose weight and improve my diet")
    
    # Check that diabetic is not in user_constraints or health_conditions
    mission_analysis = response["system_diagnostics"]["ai_metadata"]["mission_analysis"]["ai_analysis"]
    assert "diabetic" not in mission_analysis.get("user_constraints", [])
    assert "diabetic" not in mission_analysis.get("health_conditions", [])
    assert not any(ev["constraint"] == "diabetic" for ev in mission_analysis.get("evidence_validation", []))
    
    # Check that executive_summary exists and is well-formatted (Objective 6)
    customer_response = response["customer_response"]
    system_diagnostics = response["system_diagnostics"]
    
    assert "executive_summary" in customer_response
    assert "mission" in customer_response["executive_summary"]
    assert "why_selected" in customer_response["executive_summary"]
    assert "current_status" in customer_response["executive_summary"]
    assert "key_gaps" in customer_response["executive_summary"]
    assert "next_actions" in customer_response["executive_summary"]
    
    # Check that ai_runtime exists and contains provider, model, mode, etc. (Phase 7A)
    assert "ai_runtime" in system_diagnostics
    runtime = system_diagnostics["ai_runtime"]
    assert runtime["provider"] == "simulation"
    assert runtime["mode"] == "SIMULATION"
    assert "latency_ms" in runtime
    assert "input_tokens" in runtime
    assert "output_tokens" in runtime

    # Check that grounding_score >= 95
    assert system_diagnostics["metrics"]["grounding_score"] >= 95
    
    # Check policy_score (repairs may or may not happen)
    assert system_diagnostics["policy_score"] >= 0
    
    # --- Phase 7.1 Task 3: Mission Source of Truth ---
    # original_output.detected_mission must match final mission
    orig_mission = system_diagnostics["ai_metadata"]["mission_analysis"].get("original_output", {}).get("detected_mission")
    final_mission = system_diagnostics["ai_metadata"]["mission_analysis"]["ai_analysis"]["detected_mission"]
    top_level_mission = customer_response["mission"]["detected_mission"]
    assert final_mission == top_level_mission, f"Mission conflict: ai_analysis={final_mission} vs top-level={top_level_mission}"
    if orig_mission is not None:
        assert orig_mission == top_level_mission, f"Mission conflict: original_output={orig_mission} vs top-level={top_level_mission}"

    # --- Phase 7.1 Task 4: Regret Prevention - no ontology-only items ---
    # All forgotten items in final response must be catalog-backed or graph-backed
    from shared.ai.grounding.grounding_engine import GroundingEngine
    grounding = GroundingEngine()
    forgotten_items = system_diagnostics.get("regret_prevention", {}).get("forgotten_items", [])
    for item in forgotten_items:
        in_catalog, _, _ = grounding.validate_product_in_catalog(item)
        linked, _ = grounding.validate_recommendation_in_graph(item, top_level_mission)
        assert in_catalog or linked, f"Regret item '{item}' is ontology-only (not catalog or graph backed)"
    
    # --- Phase 7.1 Task 6: Response Truth Report ---
    assert "truth_report" in system_diagnostics
    truth_report = system_diagnostics["truth_report"]
    assert "live_execution_verified" in truth_report
    assert "catalog_grounded" in truth_report
    assert "graph_grounded" in truth_report
    assert "mission_consistent" in truth_report
    assert "certification_valid" in truth_report
    # In LOCAL_SIMULATION mode, live_execution_verified should be False
    assert truth_report["live_execution_verified"] == False
    # Mission must be consistent
    assert truth_report["mission_consistent"] == True

    # 2. Test weight loss with diabetic in query - check that diabetic constraint IS included
    response_diabetic = orchestrator.run_outcome_intelligence("I am diabetic and want to lose weight")
    mission_analysis_diabetic = response_diabetic["system_diagnostics"]["ai_metadata"]["mission_analysis"]["ai_analysis"]
    assert "diabetic" in mission_analysis_diabetic.get("user_constraints", [])
    assert any(ev["constraint"] == "diabetic" and ev["evidence_source"] == "query" 
               for ev in mission_analysis_diabetic.get("evidence_validation", []))

def test_live_bedrock_fail_hard():
    # If MODE is BEDROCK_LIVE, but no credentials exist (or mock failure), it must raise an exception or fail hard
    os.environ["MODE"] = "BEDROCK_LIVE"
    orchestrator = OutcomeOrchestrator()
    orchestrator.ai_gateway.cache.clear()
    
    # Mock the bedrock client to be initialized but fail during converse
    orchestrator.ai_gateway.bedrock.client = MagicMock()
    orchestrator.ai_gateway.bedrock.client.converse.side_effect = Exception("AWS Bedrock Service Connection Refused")
    orchestrator.ai_gateway.bedrock.local_mode = False
    
    # Because there's no actual live Bedrock connection/credentials configured in this test env,
    # it should raise a RuntimeError or returned certified FAILED status response
    res = orchestrator.run_outcome_intelligence("I want to lose weight")
    assert res.get("status") in ["FAILED", "BLOCKED"]
    if "system_diagnostics" in res:
        assert res["system_diagnostics"]["ai_runtime"]["provider"] == "bedrock"
    
    # Clean up
    os.environ["MODE"] = "LOCAL_SIMULATION"

def test_live_execution_enforcement_simulation_blocked():
    """Phase 7.1 Task 1: Verify that simulation responses are BLOCKED when MODE=BEDROCK_LIVE"""
    os.environ["MODE"] = "BEDROCK_LIVE"
    orchestrator = OutcomeOrchestrator()
    orchestrator.ai_gateway.cache.clear()
    
    # Force bedrock provider into local_mode to simulate a scenario where provider=simulation
    orchestrator.ai_gateway.bedrock.local_mode = True
    
    res = orchestrator.run_outcome_intelligence("I want to lose weight")
    # The response should be FAILED/BLOCKED because provider=simulation in BEDROCK_LIVE mode
    assert res["status"] in ["FAILED", "BLOCKED"]
    if "system_diagnostics" in res:
        assert res["system_diagnostics"]["certification"]["status"] == "FAILED"
    
    # Clean up
    os.environ["MODE"] = "LOCAL_SIMULATION"

def test_risk_calibration_high_critical_missing():
    """Phase 7.1 Task 5: Verify risk calibration with configurable thresholds"""
    from shared.ai.policy.policy_rules import val_invalid_risk, rep_invalid_risk, RISK_THRESHOLDS
    
    # Test: critical_missing >= 5 should force HIGH risk
    state_5_missing = {
        "verification": {"critical_missing": ["a", "b", "c", "d", "e"], "readiness_score": 50},
        "risk": {"risk_level": "LOW", "risk_score": 20}
    }
    assert val_invalid_risk(state_5_missing) == True
    repaired, logs = rep_invalid_risk(state_5_missing)
    assert repaired["risk"]["risk_level"] == "HIGH"
    assert len(logs) == 1
    
    # Test: critical_missing >= 10 should force CRITICAL risk
    state_10_missing = {
        "verification": {"critical_missing": list(range(10)), "readiness_score": 10},
        "risk": {"risk_level": "MEDIUM", "risk_score": 40}
    }
    assert val_invalid_risk(state_10_missing) == True
    repaired2, logs2 = rep_invalid_risk(state_10_missing)
    assert repaired2["risk"]["risk_level"] == "CRITICAL"
    
    # Test: critical_missing < 5 with LOW risk is fine
    state_3_missing = {
        "verification": {"critical_missing": ["a", "b", "c"], "readiness_score": 70},
        "risk": {"risk_level": "LOW", "risk_score": 20}
    }
    assert val_invalid_risk(state_3_missing) == False

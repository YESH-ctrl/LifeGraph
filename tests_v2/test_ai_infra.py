import pytest
import os
os.environ["MODE"] = "LOCAL_SIMULATION"
from shared.ai.token_tracker import TokenTracker
from shared.ai.cost_tracker import CostTracker
from shared.ai.model_router import ModelRouter
from shared.ai.response_cache import ResponseCache
from shared.ai.providers.bedrock_provider import BedrockProvider
from shared.ai.ai_gateway import AIGateway
from shared.ai.schemas import (
    DecisionDelta,
    MissionAnalysisOutput,
    CartAnalysisOutput,
    VerificationAnalysisOutput,
    RiskAnalysisOutput,
    RegretAnalysisOutput,
    SimulationAnalysisOutput,
    AuditorAnalysisOutput
)
from orchestration.master_orchestrator import OutcomeOrchestrator

def test_token_tracker():
    tracker = TokenTracker()
    assert tracker.estimate_tokens("hello world") == 2
    tracker.record_usage(10, 20)
    assert tracker.total_input_tokens == 10
    assert tracker.total_output_tokens == 20
    tracker.reset()
    assert tracker.total_input_tokens == 0

def test_cost_tracker():
    tracker = CostTracker()
    # Sonnet Pricing: input $3/1M, output $15/1M
    cost = tracker.calculate_cost("anthropic.claude-3-sonnet", 1000, 2000)
    assert cost == (1000 * 0.000003) + (2000 * 0.000015)
    assert tracker.total_cost_usd == cost
    tracker.reset()
    assert tracker.total_cost_usd == 0.0

def test_model_router():
    router = ModelRouter()
    assert router.get_model_for_agent("mission") == ModelRouter.HAIKU
    assert router.get_model_for_agent("cart") == ModelRouter.SONNET
    assert router.get_model_for_agent("auditor") == ModelRouter.SONNET

def test_response_cache():
    cache = ResponseCache()
    cache.set("model-1", "prompt-1", "system-1", "response-1")
    assert cache.get("model-1", "prompt-1", "system-1") == "response-1"
    assert cache.get("model-1", "prompt-2", "system-1") is None

def test_bedrock_provider_local_simulation():
    import os
    orig = os.environ.get("MODE")
    try:
        os.environ["MODE"] = "LOCAL_SIMULATION"
        provider = BedrockProvider()
        assert provider.test_connection() is True
        res = provider.invoke_model("anthropic.claude-3-haiku", "Evaluate user query for mission intelligence agent: Month refill")
        assert "monthly_grocery_refill" in res
    finally:
        if orig is not None:
            os.environ["MODE"] = orig
        else:
            os.environ.pop("MODE", None)

def test_ai_gateway_and_agents():
    gateway = AIGateway()
    
    # 1. Mission Agent
    mission_res = gateway.execute_agent("mission", DecisionDelta[MissionAnalysisOutput], query="month groceries", original_json="{}")
    assert mission_res.ai_analysis.detected_mission == "monthly_grocery_refill"
    assert mission_res.confidence > 0.0
    
    # 2. Cart Agent
    products_json = '[{"product_id": "organic_rolled_oats_1kg", "title": "Organic Rolled Oats 1kg", "category_path": ["Grocery", "Breakfast"], "price": 120.0}]'
    cart_res = gateway.execute_agent("cart", DecisionDelta[CartAnalysisOutput], mission_id="weight_loss_journey", products_json=products_json)
    assert cart_res.ai_analysis.mission_coherence_score >= 80
    
    # 3. Auditor Agent
    audit_res = gateway.execute_agent("auditor", DecisionDelta[AuditorAnalysisOutput], agent_logs_json="[]")
    assert audit_res.ai_analysis.overall_confidence_score > 0.0
    assert audit_res.ai_analysis.audit_score >= 90

def test_orchestrator_integration():
    orchestrator = OutcomeOrchestrator()
    response = orchestrator.run_outcome_intelligence("Need rice, atta and oil for the month")
    
    # Check that keys exist in customer_response
    customer_response = response["customer_response"]
    system_diagnostics = response["system_diagnostics"]
    
    assert "mission" in customer_response
    assert "cart" in customer_response
    assert "verification" in customer_response
    assert "risk" in customer_response
    assert "simulation" in customer_response
    
    # Check that new AI metadata has been generated
    assert "ai_metadata" in system_diagnostics
    ai_meta = system_diagnostics["ai_metadata"]
    assert "token_usage" in ai_meta
    assert "execution_cost_usd" in ai_meta
    assert "auditor_report" in system_diagnostics
    assert system_diagnostics["auditor_report"]["ai_analysis"]["audit_score"] >= 80
    
    # Check DecisionDelta features
    assert "ai_decision_log" in system_diagnostics
    assert "metrics" in system_diagnostics
    assert "decision_override_rate" in system_diagnostics["metrics"]
    assert "product_rejection_rate" in system_diagnostics["metrics"]
    assert "mission_correction_rate" in system_diagnostics["metrics"]
    assert "risk_correction_rate" in system_diagnostics["metrics"]
    assert "auditor_failure_rate" in system_diagnostics["metrics"]
    assert "capability_coverage" in system_diagnostics["metrics"]
    
    exec_summary = customer_response["executive_summary"]
    assert "capabilities" in exec_summary
    assert "products_selected" in exec_summary

def test_orchestrator_weight_loss_chocolate_rejection():
    orchestrator = OutcomeOrchestrator()
    # Query with weight loss and chocolate to trigger rejection in bedrock mock provider
    response = orchestrator.run_outcome_intelligence("I want to lose weight and need cadbury dairy milk silk")
    
    # The Cart agent should reject the chocolate item
    system_diagnostics = response["system_diagnostics"]
    assert "ai_decision_log" in system_diagnostics
    log = system_diagnostics["ai_decision_log"]
    assert "cart_agent" in log
    
    # Check that the rejection is recorded in accepted_changes
    accepted_changes = system_diagnostics["ai_metadata"]["cart_analysis"]["accepted_changes"]
    assert len(accepted_changes) > 0
    assert any("cadbury_dairy_milk_silk" in c["change"]["product_id"] for c in accepted_changes)

def test_grounding_engine():
    from shared.ai.grounding.grounding_engine import GroundingEngine
    engine = GroundingEngine()
    
    # Validate existing product in catalog
    exists, meta, err = engine.validate_product_in_catalog("cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g")
    assert exists is True
    assert "cadbury" in meta.get("title", "").lower()
    
    # Validate non-existing product
    exists, _, err = engine.validate_product_in_catalog("hallucinated_product_xyz")
    assert exists is False
    assert "not found" in err.lower()
    
    # Validate change with rejection
    change = {
        "type": "reject_product",
        "product_id": "cadbury_dairy_milk_silk_chocolate_bar_250g_pack_of_2_x_250g",
        "reason": "High sugar bar conflicts with diet"
    }
    is_val, gr_c = engine.validate_change(change, "weight_loss_journey", [])
    assert is_val is True
    assert "evidence" in gr_c
    assert len(gr_c["evidence"]["catalog"]) > 0

def test_consistency_validator():
    from shared.ai.grounding.consistency_validator import ConsistencyValidator
    validator = ConsistencyValidator()
    
    # Test valid combination
    is_con, issues, score = validator.validate_consistency(
        items_count=10,
        final_action="Proceed to Checkout",
        risk_level="LOW",
        risk_score=15,
        critical_missing_count=0,
        readiness_score=95,
        optimized_success=95
    )
    assert is_con is True
    assert score == 100
    
    # Test items_count = 0 and Proceed to Checkout contradiction
    is_con, issues, score = validator.validate_consistency(
        items_count=0,
        final_action="Proceed to Checkout",
        risk_level="LOW",
        risk_score=15,
        critical_missing_count=0,
        readiness_score=95,
        optimized_success=95
    )
    assert is_con is False
    assert score < 100
    assert any("empty" in i.lower() for i in issues)

def test_success_calibration():
    from shared.ai.grounding.success_calibration import SuccessCalibrator
    calibrator = SuccessCalibrator()
    
    # Test suggested success within bounds
    cal_score, explanation = calibrator.calibrate_success_score(
        readiness_score=80,
        risk_score=20,
        mission_coherence_score=90,
        ai_suggested_success=82
    )
    assert cal_score == 82
    assert "grounded within valid bounds" in explanation
    
    # Test suggested success violating upper bound
    cal_score, explanation = calibrator.calibrate_success_score(
        readiness_score=80,
        risk_score=20,
        mission_coherence_score=90,
        ai_suggested_success=100
    )
    assert cal_score < 100
    assert "exceeded reality constraint cap" in explanation

def test_orchestrator_trust_metrics_and_caps():
    orchestrator = OutcomeOrchestrator()
    response = orchestrator.run_outcome_intelligence("Need rice, atta and oil for the month")
    
    # Check that Phase 3 trust metrics exist in system_diagnostics metrics
    metrics = response["system_diagnostics"]["metrics"]
    assert "grounding_score" in metrics
    assert "reality_score" in metrics
    assert "consistency_score" in metrics
    assert "catalog_validity_score" in metrics
    assert "graph_validity_score" in metrics
    
    assert metrics["grounding_score"] >= 0
    assert metrics["reality_score"] >= 0
    assert metrics["consistency_score"] >= 0

def test_policy_engine_empty_cart_repair():
    from shared.ai.policy.policy_engine import PolicyEngine
    engine = PolicyEngine()
    
    # Construct inconsistent state for empty cart
    state = {
        "cart": {
            "items_count": 0
        },
        "verification": {
            "readiness_score": 55,
            "critical_missing": []
        },
        "risk": {
            "risk_level": "LOW",
            "risk_score": 15
        },
        "simulation": {
            "optimized_success": 85,
            "current_success": 55,
            "improvement": 30
        },
        "final_recommendation": {
            "action": "Proceed to Checkout",
            "message": "Looks good."
        },
        "reasoning": [],
        "ai_metadata": {
            "metrics": {}
        }
    }
    
    final_state, cert = engine.evaluate_and_repair(state)
    
    # Verify auto-repair applied correctly
    assert final_state["verification"]["readiness_score"] == 0
    assert final_state["risk"]["risk_level"] == "HIGH"
    assert final_state["risk"]["risk_score"] == 100
    assert final_state["simulation"]["optimized_success"] == 0
    assert final_state["final_recommendation"]["action"] == "Review Cart"
    
    # Verify certification metadata
    assert cert["status"] == "AUTO_REPAIRED"
    assert cert["repaired"] is True
    assert cert["trust_level"] == "AUTO_REPAIRED"
    assert len(cert["repair_log"]) > 0

def test_policy_engine_trusted():
    from shared.ai.policy.policy_engine import PolicyEngine
    engine = PolicyEngine()
    
    # Construct a consistent state
    state = {
        "cart": {
            "items_count": 5
        },
        "verification": {
            "readiness_score": 90,
            "critical_missing": [],
            "recommended_products": []
        },
        "risk": {
            "risk_level": "LOW",
            "risk_score": 10
        },
        "simulation": {
            "optimized_success": 95,
            "current_success": 90,
            "improvement": 5
        },
        "final_recommendation": {
            "action": "Proceed to Checkout",
            "message": "Perfect cart."
        },
        "reasoning": [],
        "regret_prevention": {
            "forgotten_items": []
        },
        "ai_metadata": {
            "metrics": {}
        },
        "grounding_score": 100,
        "catalog_validity_score": 100,
        "graph_validity_score": 100,
        "reality_score": 100,
        "consistency_score": 100
    }
    
    final_state, cert = engine.evaluate_and_repair(state)
    
    assert cert["status"] == "TRUSTED"
    assert cert["repaired"] is False
    assert cert["trust_level"] == "TRUSTED"
    assert len(cert["repair_log"]) == 0

def test_policy_engine_hard_failure():
    from shared.ai.policy.policy_engine import PolicyEngine
    engine = PolicyEngine()
    
    # State with unrepairable leak (raw UUID in reasoning)
    state = {
        "cart": {
            "items_count": 5
        },
        "verification": {
            "readiness_score": 90,
            "critical_missing": [],
            "recommended_products": []
        },
        "risk": {
            "risk_level": "LOW",
            "risk_score": 10
        },
        "simulation": {
            "optimized_success": 95,
            "current_success": 90,
            "improvement": 5
        },
        "final_recommendation": {
            "action": "Proceed to Checkout",
            "message": "Perfect cart."
        },
        "reasoning": ["Referenced UUID: 123e4567-e89b-12d3-a456-426614174000"],
        "regret_prevention": {
            "forgotten_items": []
        },
        "ai_metadata": None
    }
    
    final_state, cert = engine.evaluate_and_repair(state)
    assert final_state["status"] == "BLOCKED"
    assert cert["status"] == "FAILED"
    assert cert["repaired"] is False
    assert len(cert["errors"]) > 0

def test_orchestrator_production_certification():
    orchestrator = OutcomeOrchestrator()
    response = orchestrator.run_outcome_intelligence("Need rice, atta and oil for the month")
    
    # Verify response certification wrapper
    system_diagnostics = response["system_diagnostics"]
    assert "certification" in system_diagnostics
    assert "repair_log" in system_diagnostics
    assert "trust_level" in system_diagnostics
    assert "policy_score" in system_diagnostics
    
    cert = system_diagnostics["certification"]
    assert cert["status"] in ["TRUSTED", "WARNING", "AUTO_REPAIRED"]
    assert "policy_score" in cert
    assert "trust_level" in cert

def test_diagnostics_endpoint():
    from fastapi.testclient import TestClient
    from local_app import app
    client = TestClient(app)
    
    response = client.get("/ai/diagnostics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "mode" in data
    assert "active_models" in data
    assert "available_models" in data
    assert "failure_count" in data
    assert "fallback_count" in data




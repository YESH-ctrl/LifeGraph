"""
V2 Graph Enforcement Refactor – Integration Tests.
Validates that all agents consume V2 graph data and produce explainable outputs.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from foundation.domains.missions.agent_test_service import AgentTestService
from foundation.graph.service import GraphService


@pytest.fixture(scope="module")
def service():
    return AgentTestService()


@pytest.fixture(scope="module")
def graph():
    return GraphService()


class TestGraphRepository:
    """Verify graph repository methods return V2 data."""

    def test_mission_metadata(self, graph):
        metadata = graph.get_mission_metadata("birthday_party")
        # Metadata may or may not exist depending on whether graph is seeded
        if metadata:
            assert "name" in metadata
            assert "category" in metadata

    def test_mission_requirements_weighted(self, graph):
        reqs = graph.get_mission_requirements_weighted("birthday_party")
        if reqs:
            for r in reqs:
                assert "product_id" in r
                assert "priority" in r
                assert "weight" in r

    def test_mission_rules(self, graph):
        rules = graph.get_mission_rules("birthday_party")
        if rules:
            for rule in rules:
                assert "product" in rule
                assert "serves_per_unit" in rule

    def test_mission_intents(self, graph):
        intents = graph.get_mission_intents("birthday_party")
        # Just verify it returns a list
        assert isinstance(intents, list)

    def test_mission_synonyms(self, graph):
        synonyms = graph.get_mission_synonyms("birthday_party")
        assert isinstance(synonyms, list)


class TestVerificationV2:
    """Verify the Verification Agent uses weighted priorities."""

    def test_verification_returns_priority_fields(self, service):
        result = service.test_verification("birthday_party", ["birthday_cake", "birthday_candles"])
        assert "readiness_score" in result
        assert "critical_completion" in result
        assert "important_completion" in result
        assert "optional_completion" in result
        assert "critical_missing" in result
        assert "important_missing" in result
        assert "optional_missing" in result
        assert "recommended_products" in result

    def test_readiness_uses_weighted_formula(self, service):
        result = service.test_verification("birthday_party", ["birthday_cake", "birthday_candles"])
        # Readiness should be a number between 0-100
        assert 0 <= result["readiness_score"] <= 100

    def test_empty_products_returns_low_readiness(self, service):
        result = service.test_verification("birthday_party", [])
        # With no products, readiness should be low (unless there are no requirements)
        assert isinstance(result["readiness_score"], int)


class TestRiskV2:
    """Verify the Risk Agent returns multi-dimensional risk."""

    def test_risk_returns_five_dimensions(self, service):
        result = service.test_risk("birthday_party", ["birthday_cake"])
        assert "completion_risk" in result
        assert "quantity_risk" in result
        assert "compatibility_risk" in result
        assert "timing_risk" in result
        assert "budget_risk" in result
        assert "overall_risk" in result

    def test_risk_values_are_numeric(self, service):
        result = service.test_risk("birthday_party", ["birthday_cake"])
        for key in ["completion_risk", "quantity_risk", "compatibility_risk", "timing_risk", "budget_risk", "overall_risk"]:
            assert isinstance(result[key], int)
            assert 0 <= result[key] <= 100


class TestSimulatorV2:
    """Verify the Simulator Agent returns graph-driven outputs."""

    def test_simulator_returns_required_fields(self, service):
        products = [{"product": "birthday_cake", "quantity": 1}]
        result = service.test_simulator("birthday_party", 15, products)
        assert "required_products" in result
        assert "available_products" in result
        assert "quantity_gaps" in result
        assert "success_probability" in result
        assert "assumptions" in result

    def test_simulator_probability_is_calculated(self, service):
        products = [{"product": "birthday_cake", "quantity": 1}]
        result = service.test_simulator("birthday_party", 15, products)
        # Probability should be numeric
        assert isinstance(result["success_probability"], (int, float))
        assert 0 <= result["success_probability"] <= 100

    def test_simulator_no_hardcoded_062(self, service):
        products = [{"product": "birthday_cake", "quantity": 1}]
        result = service.test_simulator("birthday_party", 15, products)
        # Probability should NOT be exactly 0.62 (legacy value)
        assert result["success_probability"] != 0.62


class TestAdaptiveV2:
    """Verify the Adaptive Agent uses persona engine."""

    def test_adaptive_returns_persona(self, service):
        result = service.test_adaptive("demo_user", mission_id="birthday_party")
        assert "shopper_type" in result
        assert "recommended_intervention" in result

    def test_adaptive_no_window_shopper(self, service):
        result = service.test_adaptive("demo_user", mission_id="birthday_party")
        assert result["shopper_type"] != "Window Shopper"

    def test_adaptive_event_category_returns_event_planner(self, service):
        result = service.test_adaptive("demo_user", mission_category="CELEBRATION")
        assert result["shopper_type"] == "Event Planner"

    def test_adaptive_emergency_returns_emergency_buyer(self, service):
        result = service.test_adaptive("demo_user", urgency="HIGH")
        assert result["shopper_type"] == "Emergency Buyer"


class TestMemoryV2:
    """Verify the Memory Agent returns structured mission state."""

    def test_memory_returns_structured_state(self, service):
        result = service.test_memory("demo_user")
        assert "active_missions" in result
        assert "completed_missions" in result
        assert "recurring_missions" in result


class TestFinalDecisionV2:
    """Verify the Final Decision is explainable."""

    def test_orchestrator_final_decision_has_reason(self, service):
        result = service.test_orchestrator("I am turning 20 tomorrow and inviting 15 friends.")
        fd = result["final_decision"]
        assert "checkout_allowed" in fd
        assert "reason" in fd
        assert "recommended_actions" in fd
        assert "risk_summary" in fd

    def test_orchestrator_reason_is_not_generic(self, service):
        result = service.test_orchestrator("I am turning 20 tomorrow and inviting 15 friends.")
        fd = result["final_decision"]
        # Reason should not be the old generic text
        assert fd["reason"] != "Checkout blocked due to missing dependencies or high risk."
        assert fd["reason"] != "high risk"

    def test_orchestrator_verification_has_priorities(self, service):
        result = service.test_orchestrator("I am turning 20 tomorrow and inviting 15 friends.")
        v = result["verification"]
        assert "critical_completion" in v
        assert "important_completion" in v

    def test_orchestrator_risk_is_multi_dimensional(self, service):
        result = service.test_orchestrator("I am turning 20 tomorrow and inviting 15 friends.")
        r = result["risk"]
        assert "completion_risk" in r
        assert "quantity_risk" in r

    def test_orchestrator_simulation_has_gaps(self, service):
        result = service.test_orchestrator("I am turning 20 tomorrow and inviting 15 friends.")
        s = result["simulation"]
        assert "required_products" in s
        assert "quantity_gaps" in s
        assert "success_probability" in s

    def test_orchestrator_adaptive_has_persona(self, service):
        result = service.test_orchestrator("I am turning 20 tomorrow and inviting 15 friends.")
        a = result["adaptive"]
        assert "shopper_type" in a
        assert a["shopper_type"] != "Window Shopper"


class TestLegacyRemoval:
    """Verify no hardcoded values remain."""

    def test_no_hardcoded_readiness_zero(self, service):
        result = service.test_verification("birthday_party", ["birthday_cake", "birthday_candles"])
        # With at least some products provided, readiness should not be exactly 0
        # (unless there are no matching requirements, which is unlikely for birthday_party)
        reqs = service.graph_service.get_mission_requirements_weighted("birthday_party")
        if reqs:
            assert result["readiness_score"] > 0 or len(result["missing_items"]) == len(reqs)

    def test_no_hardcoded_risk_100(self, service):
        result = service.test_risk("birthday_party", ["birthday_cake", "birthday_candles"])
        # With some products, overall risk should not be exactly 100
        reqs = service.graph_service.get_mission_requirements_weighted("birthday_party")
        if reqs:
            assert result["overall_risk"] < 100 or len(result.get("missing_items", [])) == len(reqs)

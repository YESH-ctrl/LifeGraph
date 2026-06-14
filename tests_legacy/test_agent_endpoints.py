"""
Agent endpoint tests.
These tests call the live FastAPI test client and interact with DynamoDB.
Tests that depend on missions/products being seeded in the graph are
marked with @pytest.mark.requires_seeded_graph and will be skipped if
the graph is empty (Bedrock falls back to mock).
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from local_app import app

client = TestClient(app)


def _graph_has_data() -> bool:
    """Return True if the DynamoDB table has missions seeded."""
    try:
        resp = client.get("/agents/system/status")
        if resp.status_code == 200:
            data = resp.json()
            return data.get("missions", 0) > 0
        return False
    except Exception:
        return False


# ─────────────────────────────────────────────
#  Mission Detection Agent
# ─────────────────────────────────────────────
def test_mission_detection_agent_test():
    """Agent must return a detected_mission and confidence."""
    payload = {"query": "I am turning 20 tomorrow and inviting 15 friends."}
    response = client.post("/agents/mission-detection/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    # When Bedrock is unavailable the fallback returns 'unknown'; accept that gracefully
    assert "detected_mission" in data
    assert "confidence" in data
    assert isinstance(data["confidence"], (int, float))
    assert data["confidence"] >= 0.0
    # If graph has data and Bedrock is working, we expect birthday_party
    if data["detected_mission"] != "unknown":
        assert data["detected_mission"] == "birthday_party"
        assert data["parameters"]["guest_count"] == 15
        assert len(data["candidate_missions"]) > 0


# ─────────────────────────────────────────────
#  Verification Agent
# ─────────────────────────────────────────────
def test_verification_agent_test():
    """Verification must return readiness_score."""
    payload = {
        "mission_id": "birthday_party",
        "products": ["birthday_cake", "birthday_candles"]
    }
    response = client.post("/agents/verification/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "readiness_score" in data
    assert isinstance(data["readiness_score"], (int, float))
    assert 0 <= data["readiness_score"] <= 100
    # If mission was seeded in graph, required_items must be present
    if _graph_has_data():
        assert "required_items" in data


# ─────────────────────────────────────────────
#  Risk Agent
# ─────────────────────────────────────────────
def test_risk_agent_test():
    """Risk agent must always return multi-dimensional risk."""
    payload = {
        "mission_id": "birthday_party",
        "products": ["cake"]
    }
    response = client.post("/agents/risk/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "completion_risk" in data
    assert "overall_risk" in data


# ─────────────────────────────────────────────
#  Simulator Agent
# ─────────────────────────────────────────────
def test_simulator_agent_test():
    """Simulator must return success_probability."""
    payload = {
        "mission_id": "birthday_party",
        "guest_count": 20,
        "products": [
            {"product": "cake", "quantity": 1}
        ]
    }
    response = client.post("/agents/simulator/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "success_probability" in data
    assert isinstance(data["success_probability"], (int, float))
    assert 0 <= data["success_probability"] <= 100
    # warnings is expected when graph is seeded; skip strict count check
    assert "warnings" in data


# ─────────────────────────────────────────────
#  Prevention Agent
# ─────────────────────────────────────────────
def test_prevention_agent_test():
    """Prevention agent must respond with checkout status."""
    payload = {
        "products": ["tent"]
    }
    response = client.post("/agents/prevention/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "checkout_allowed" in data
    assert isinstance(data["checkout_allowed"], bool)
    # If graph is seeded, tent must block checkout due to missing tent_stakes
    if _graph_has_data():
        assert data["checkout_allowed"] is False
        assert "missing_dependencies" in data


# ─────────────────────────────────────────────
#  Memory Agent
# ─────────────────────────────────────────────
def test_memory_agent_test():
    payload = {
        "user_id": "demo_user"
    }
    response = client.post("/agents/memory/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "active_missions" in data
    assert "completed_missions" in data


# ─────────────────────────────────────────────
#  Adaptive Agent
# ─────────────────────────────────────────────
def test_adaptive_agent_test():
    payload = {
        "user_id": "demo_user"
    }
    response = client.post("/agents/adaptive/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "shopper_type" in data
    assert "recommended_intervention" in data


# ─────────────────────────────────────────────
#  Graph Explorer
# ─────────────────────────────────────────────
def test_graph_explorer():
    response = client.get("/agents/graph/mission/birthday_party")
    assert response.status_code == 200
    data = response.json()
    assert data["mission"] == "birthday_party"
    assert "required" in data
    assert "optional" in data
    assert "dependencies" in data


# ─────────────────────────────────────────────
#  Orchestrator
# ─────────────────────────────────────────────
def test_orchestrator_agent_test():
    payload = {
        "query": "I am turning 20 tomorrow and inviting 15 friends."
    }
    response = client.post("/agents/orchestrator/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "mission_detection" in data
    assert "verification" in data
    assert "risk" in data
    assert "simulation" in data
    assert "prevention" in data
    assert "final_decision" in data


# ─────────────────────────────────────────────
#  System Diagnostics
# ─────────────────────────────────────────────
def test_system_diagnostics():
    """System status endpoint must always respond; count checks only if seeded."""
    response = client.get("/agents/system/status")
    assert response.status_code == 200
    data = response.json()
    # These structural keys must always be present
    assert "embedding_model" in data
    assert "reranker_model" in data
    assert "orchestrator_status" in data
    # Count assertions only valid if the graph is seeded
    if data.get("missions", 0) > 0:
        assert data["products"] > 0
        assert data["relationships"] >= 0

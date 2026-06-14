import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add src to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from local_app import app

client = TestClient(app)

def test_mission_detection_agent_test():
    payload = {"query": "I am turning 20 tomorrow and inviting 15 friends."}
    response = client.post("/agents/mission-detection/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["detected_mission"] == "birthday_party"
    assert data["confidence"] > 0.0
    assert len(data["candidate_missions"]) > 0
    assert data["parameters"]["guest_count"] == 15

def test_verification_agent_test():
    payload = {
        "mission_id": "birthday_party",
        "products": ["birthday_cake", "birthday_candles"]
    }
    response = client.post("/agents/verification/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "readiness_score" in data
    assert len(data["required_items"]) > 0
    assert "birthday_cake" in data["required_items"]

def test_risk_agent_test():
    payload = {
        "mission_id": "birthday_party",
        "products": ["cake"]
    }
    response = client.post("/agents/risk/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "completion_risk" in data
    assert "overall_risk" in data

def test_simulator_agent_test():
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
    assert len(data["warnings"]) > 0

def test_prevention_agent_test():
    payload = {
        "products": ["tent"]
    }
    response = client.post("/agents/prevention/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["checkout_allowed"] is False
    assert "tent_stakes" in data["missing_dependencies"]

def test_memory_agent_test():
    payload = {
        "user_id": "demo_user"
    }
    response = client.post("/agents/memory/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "active_missions" in data
    assert "completed_missions" in data

def test_adaptive_agent_test():
    payload = {
        "user_id": "demo_user"
    }
    response = client.post("/agents/adaptive/test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "shopper_type" in data
    assert "recommended_intervention" in data

def test_graph_explorer():
    response = client.get("/agents/graph/mission/birthday_party")
    assert response.status_code == 200
    data = response.json()
    assert data["mission"] == "birthday_party"
    assert "required" in data
    assert "optional" in data
    assert "dependencies" in data

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

def test_system_diagnostics():
    response = client.get("/agents/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["missions"] > 0
    assert data["products"] > 0
    assert data["relationships"] > 0
    assert "embedding_model" in data
    assert "reranker_model" in data
    assert data["orchestrator_status"] == "healthy"

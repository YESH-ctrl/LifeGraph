import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add src to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from local_app import app

client = TestClient(app)

def test_happy_path_mission_execute():
    """Verify that a standard execution runs the full pipeline and returns successful responses."""
    payload = {
        "userId": "USER001",
        "missionId": "BIRTHDAY",
        "cartId": "CART001",
        "context": {
            "budget": 1500,
            "urgency": "LOW",
            "location": "HYDERABAD"
        }
    }
    
    response = client.post("/mission/execute", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    
    res_data = data["data"]
    assert res_data["mission"]["missionId"] == "BIRTHDAY"
    assert "verification" in res_data
    assert "risk" in res_data
    assert "simulation" in res_data
    assert "adaptiveDecision" in res_data
    assert "checkout" in res_data
    assert res_data["checkout"]["allowCheckout"] is True
    assert len(res_data["recommendations"]) > 0

def test_high_risk_and_incomplete_cart():
    """Verify that a high urgency request combined with missing items activates strict mode and checkout checks."""
    payload = {
        "userId": "USER001",
        "missionId": "BIRTHDAY",
        "cartId": "CART001",
        "context": {
            "budget": 100,
            "urgency": "HIGH",
            "location": "HYDERABAD"
        }
    }
    
    response = client.post("/mission/execute", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    
    res_data = data["data"]
    # Urgency HIGH should trigger strict mode in adaptive decision
    assert res_data["adaptiveDecision"]["strictMode"] is True
    
    # Under strict mode, verification score of 50 is less than 80, blocking checkout
    assert res_data["checkout"]["allowCheckout"] is False
    assert len(res_data["checkout"]["blockingIssues"]) > 0
    assert "strict mode active" in res_data["checkout"]["blockingIssues"][0].lower()

def test_missing_required_fields():
    """Verify validation handles missing inputs correctly."""
    payload = {
        "userId": "USER001"
    }
    response = client.post("/mission/execute", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()

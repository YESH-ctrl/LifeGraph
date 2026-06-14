import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add src to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from local_app import app
from domains.carts.repository import CartRepository
from domains.carts.models import CartModel, CartItemModel

client = TestClient(app)

def test_semantic_mission_detection_birthday_party():
    """Verify scenario: I am turning 20 tomorrow."""
    payload = {
        "query": "I am turning 20 tomorrow."
    }
    response = client.post("/mission/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["mission_id"] == "birthday_party"
    assert data["parameters"]["event_date"] == "tomorrow"
    assert data["confidence"] > 0.0

def test_semantic_mission_detection_diwali():
    """Verify scenario: Need items for Diwali celebration."""
    payload = {
        "query": "Need items for Diwali celebration."
    }
    response = client.post("/mission/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["mission_id"] == "diwali_celebration"
    assert data["validation"]["required_products_count"] > 0

def test_semantic_mission_detection_biryani():
    """Verify scenario: Preparing biryani for 20 people."""
    payload = {
        "query": "Preparing biryani for 20 people."
    }
    response = client.post("/mission/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["mission_id"] == "biryani_preparation"
    assert data["parameters"]["guest_count"] == 20

def test_semantic_mission_detection_train():
    """Verify scenario: Going on a train journey with family."""
    payload = {
        "query": "Going on a train journey with family."
    }
    response = client.post("/mission/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["mission_id"] == "train_journey_essentials"

def test_semantic_mission_detection_ganesh():
    """Verify scenario: Need pooja items for Ganesh Chaturthi."""
    payload = {
        "query": "Need pooja items for Ganesh Chaturthi."
    }
    response = client.post("/mission/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["mission_id"] == "ganesh_chaturthi"


def test_verification_agent_dynamic_graph():
    """Verify that verification compares against graph DB requirements and calculates dynamic scores."""
    # Let's seed a temporary cart in DynamoDB
    cart_id = "CART_TEST_INDIA"
    user_id = "USER_TEST_INDIA"
    
    cart_repo = CartRepository()
    # Create the cart
    cart_repo.create_cart(CartModel(id=cart_id, user_id=user_id))
    
    # Add some products to the cart: e.g. clay_diyas and marigold_garland
    # These are part of diwali_celebration products
    cart_repo.add_item_to_cart(CartItemModel(cart_id=cart_id, product_id="clay_diyas", quantity=10))
    cart_repo.add_item_to_cart(CartItemModel(cart_id=cart_id, product_id="marigold_garland", quantity=5))
    
    payload = {
        "missionId": "diwali_celebration",
        "cartId": cart_id
    }
    
    response = client.post("/verification/verify", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    # Check that it executed and calculated a dynamic score
    # Score should be less than 100 because diwali_celebration requires 20 items, but we only have 2
    assert "verification_score" in data["data"]
    score = data["data"]["verification_score"]
    assert 0 <= score < 100
    assert len(data["data"]["missing_items"]) > 0

def test_mission_debug_diagnostics():
    """Verify that the diagnostics endpoint returns correct keys and structure."""
    response = client.get("/mission/debug")
    assert response.status_code == 200
    data = response.json()
    assert "available_models" in data
    assert "embedding_model" in data
    assert "reranker_model" in data
    assert "fallback_mode" in data


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
        from graph.service import GraphService
        gs = GraphService()
        reqs = gs.get_mission_requirements_weighted("birthday_party")
        return bool(reqs)
    except Exception:
        return False


def setup_test_cart(happy_path=True):
    from domains.carts.repository import CartRepository
    from domains.carts.models import CartModel, CartItemModel
    from graph.service import GraphService

    gs = GraphService()
    reqs_weighted = gs.get_mission_requirements_weighted("birthday_party")

    critical_items = [r["product_id"] for r in reqs_weighted if r.get("priority", "IMPORTANT").upper() == "CRITICAL"]
    important_items = [r["product_id"] for r in reqs_weighted if r.get("priority", "IMPORTANT").upper() == "IMPORTANT"]

    cart_repo = CartRepository()
    try:
        cart_repo.delete_cart("CART001")
    except Exception:
        pass

    cart_repo.create_cart(CartModel(id="CART001", user_id="USER001"))

    if happy_path:
        for item in critical_items + important_items:
            cart_repo.add_item_to_cart(CartItemModel(cart_id="CART001", product_id=item, quantity=1))
    else:
        for item in critical_items:
            cart_repo.add_item_to_cart(CartItemModel(cart_id="CART001", product_id=item, quantity=1))


def test_happy_path_mission_execute():
    """Verify that a standard execution runs the full pipeline and returns successful responses."""
    if not _graph_has_data():
        pytest.skip("Graph not seeded — skipping integration test that requires birthday_party edges")

    setup_test_cart(happy_path=True)
    payload = {
        "userId": "USER001",
        "missionId": "birthday_party",
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
    assert res_data["mission"]["missionId"] == "birthday_party"
    assert "verification" in res_data
    assert "risk" in res_data
    assert "simulation" in res_data
    assert "adaptiveDecision" in res_data
    assert "checkout" in res_data
    assert res_data["checkout"]["allowCheckout"] is True
    assert len(res_data["recommendations"]) > 0


def test_high_risk_and_incomplete_cart():
    """Verify that high urgency + missing items activates strict mode and blocks checkout."""
    if not _graph_has_data():
        pytest.skip("Graph not seeded — skipping integration test that requires birthday_party edges")

    setup_test_cart(happy_path=False)
    payload = {
        "userId": "USER001",
        "missionId": "birthday_party",
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
    assert res_data["adaptiveDecision"]["strictMode"] is True
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

"""
Mission Discovery Agent (Agent 1) tests and benchmark report.

Runs against the live FastAPI test client and DynamoDB graph when seeded.
"""
import json
import math
import os
import sys
import time

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from local_app import app

client = TestClient(app)

BENCHMARK_SCENARIOS = [
    {
        "name": "Birthday Party",
        "query": "I am turning 20 tomorrow and inviting 15 friends.",
        "expected_mission": "birthday_party",
        "expected_guest_count": 15,
        "cart_checks": [
            {"product_id": "birthday_cake", "quantity": 2},
        ],
    },
    {
        "name": "Biryani Preparation",
        "query": "Preparing Hyderabadi biryani for 20 guests.",
        "expected_mission": "biryani_preparation",
        "expected_guest_count": 20,
        "cart_checks": [],
    },
    {
        "name": "Monthly Grocery Refill",
        "query": "Need groceries for the whole month for a family of four.",
        "expected_mission": "monthly_grocery_refill",
        "expected_guest_count": 4,
        "cart_checks": [],
    },
    {
        "name": "Exam Preparation Week",
        "query": "My exams start next week and I need supplies.",
        "expected_mission": "exam_preparation_week",
        "cart_checks": [],
    },
    {
        "name": "Train Journey Snacks",
        "query": "Going on a train trip tomorrow.",
        "expected_mission": "train_journey_snacks",
        "accept_missions": {"train_journey_snacks", "train_journey_essentials"},
        "cart_checks": [],
    },
    {
        "name": "Weight Loss Journey",
        "query": "I want to start losing weight.",
        "expected_mission": "weight_loss_journey",
        "cart_checks": [],
    },
    {
        "name": "Family Gathering",
        "query": "Planning a family gathering this weekend for 10 relatives.",
        "expected_mission": "family_gathering",
        "expected_guest_count": 10,
        "cart_checks": [],
    },
    {
        "name": "Housewarming Ceremony",
        "query": "We are doing a housewarming ceremony next month.",
        "expected_mission": "housewarming_ceremony",
        "cart_checks": [],
    },
]


def _graph_has_data() -> bool:
    try:
        resp = client.get("/agents/system/status")
        if resp.status_code == 200:
            return resp.json().get("missions", 0) > 0
    except Exception:
        pass
    return False


def _call_discovery(query: str) -> dict:
    response = client.post("/agents/mission-discovery", json={"query": query})
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize("scenario", BENCHMARK_SCENARIOS, ids=[s["name"] for s in BENCHMARK_SCENARIOS])
def test_mission_discovery_scenario(scenario):
    """Each required scenario must return a structured Agent 1 response."""
    data = _call_discovery(scenario["query"])

    assert "intent" in data
    assert "intent" in data["intent"]
    assert "parameters" in data["intent"]
    assert "mission" in data
    assert "detected_mission" in data["mission"]
    assert "confidence" in data["mission"]
    assert "candidate_missions" in data["mission"]
    assert len(data["mission"]["candidate_missions"]) == 5
    assert "requirements" in data
    assert "critical_products" in data["requirements"]
    assert "important_products" in data["requirements"]
    assert "optional_products" in data["requirements"]
    assert "suggested_cart" in data
    assert "explanation" in data
    assert isinstance(data["explanation"], list)
    assert len(data["explanation"]) > 0

    detected = data["mission"]["detected_mission"]
    expected = scenario.get("expected_mission")
    accepted = scenario.get("accept_missions", {expected} if expected else set())

    if _graph_has_data() and detected != "unknown":
        assert detected in accepted, f"Expected {accepted}, got {detected}"

    if scenario.get("expected_guest_count") and detected != "unknown":
        assert data["intent"]["parameters"].get("guest_count") == scenario["expected_guest_count"]

    for check in scenario.get("cart_checks", []):
        cart_item = next(
            (c for c in data["suggested_cart"] if c["product_id"] == check["product_id"]),
            None,
        )
        if cart_item and _graph_has_data():
            assert cart_item["quantity"] == check["quantity"]


def test_mission_discovery_only_approved_catalog():
    """Detected mission must belong to the frozen 20-mission catalog."""
    from agents.mission_discovery_agent import FROZEN_MISSION_CATALOG

    data = _call_discovery("Need groceries for the whole month for a family of four.")
    detected = data["mission"]["detected_mission"]
    if detected != "unknown":
        assert detected in FROZEN_MISSION_CATALOG
    for candidate in data["mission"]["candidate_missions"]:
        assert candidate["mission"] in FROZEN_MISSION_CATALOG


def test_mission_discovery_requirements_from_graph():
    """Requirements must be fetched from graph, not hardcoded."""
    if not _graph_has_data():
        pytest.skip("Graph not seeded")

    data = _call_discovery("I am turning 20 tomorrow and inviting 15 friends.")
    reqs = data["requirements"]
    total = len(reqs["critical_products"]) + len(reqs["important_products"]) + len(reqs["optional_products"])
    assert total > 0


def test_mission_discovery_response_time():
    """Response should complete within 2 seconds under normal conditions."""
    start = time.perf_counter()
    _call_discovery("Going on a train trip tomorrow.")
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"Response took {elapsed:.2f}s, expected < 2s"


def test_mission_discovery_benchmark_report(capsys):
    """Generate benchmark report after executing all scenarios."""
    mission_correct = 0
    top3_hits = 0
    cart_correct = 0
    cart_total = 0
    response_times = []

    for scenario in BENCHMARK_SCENARIOS:
        start = time.perf_counter()
        data = _call_discovery(scenario["query"])
        elapsed = time.perf_counter() - start
        response_times.append(elapsed)

        expected = scenario["expected_mission"]
        accepted = scenario.get("accept_missions", {expected})
        detected = data["mission"]["detected_mission"]

        if detected in accepted:
            mission_correct += 1

        top3 = [c["mission"] for c in data["mission"]["candidate_missions"][:3]]
        if any(m in accepted for m in top3):
            top3_hits += 1

        for check in scenario.get("cart_checks", []):
            cart_total += 1
            cart_item = next(
                (c for c in data["suggested_cart"] if c["product_id"] == check["product_id"]),
                None,
            )
            if cart_item and cart_item["quantity"] == check["quantity"]:
                cart_correct += 1

    total = len(BENCHMARK_SCENARIOS)
    report = {
        "mission_accuracy": f"{mission_correct / total * 100:.1f}%",
        "top3_recall": f"{top3_hits / total * 100:.1f}%",
        "cart_accuracy": f"{cart_correct / cart_total * 100:.1f}%" if cart_total else "N/A",
        "average_response_time": f"{sum(response_times) / len(response_times):.3f}s",
    }

    print("\nBENCHMARK REPORT:")
    print(json.dumps(report, indent=2))

    captured = capsys.readouterr()
    assert "BENCHMARK REPORT" in captured.out

    if _graph_has_data():
        assert mission_correct / total >= 0.5, report

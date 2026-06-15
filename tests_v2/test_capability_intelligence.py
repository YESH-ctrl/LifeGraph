import pytest
from engines.domains.capability_intelligence_service import CapabilityIntelligenceService

def test_get_capabilities_for_mission():
    service = CapabilityIntelligenceService()
    caps = service.get_capabilities_for_mission("weight_loss_journey")
    assert "protein_intake" in caps
    assert "fiber_intake" in caps
    assert "calorie_control" in caps
    assert "satiety" in caps
    assert "hydration" in caps

    caps_refill = service.get_capabilities_for_mission("monthly_grocery_refill")
    assert "pantry_refill" in caps_refill
    assert "household_consumables" in caps_refill

def test_check_product_capability_coverage():
    service = CapabilityIntelligenceService()
    
    product_oats = {
        "title": "Organic Rolled Oats 1kg",
        "subcategory": "Breakfast Oats",
        "category_path": ["Grocery", "Breakfast"],
        "semanticTags": ["organic", "whole grain", "fiber"]
    }
    
    # Oats covers whole_foods and fiber_intake
    assert service.check_product_capability_coverage(product_oats, "fiber_intake") is True
    assert service.check_product_capability_coverage(product_oats, "whole_foods") is True
    assert service.check_product_capability_coverage(product_oats, "hydration") is False

    product_protein = {
        "title": "Whey Protein Powder",
        "subcategory": "Supplements",
        "category_path": ["Health", "Sports Nutrition"],
        "semanticTags": ["protein", "high protein"]
    }
    assert service.check_product_capability_coverage(product_protein, "protein_intake") is True
    assert service.check_product_capability_coverage(product_protein, "household_consumables") is False

def test_score_product():
    service = CapabilityIntelligenceService()
    
    product = {
        "id": "organic_rolled_oats_1kg",
        "title": "Organic Rolled Oats 1kg",
        "subcategory": "Breakfast Oats",
        "category_path": ["Grocery", "Breakfast"],
        "semanticTags": ["organic", "whole grain", "fiber"],
        "price": 120.0,
        "primary_missions": ["weight_loss_journey"]
    }
    
    # Required/optional sets
    required_pids = {"organic_rolled_oats_1kg"}
    optional_pids = set()
    
    scores = service.score_product(product, "weight_loss_journey", required_pids, optional_pids)
    
    assert scores["final_score"] > 0
    assert scores["capability_score"] == (2.0 / 5.0 * 100.0) # fiber_intake, satiety
    assert scores["nutrition_score"] == 95.0 # organic / oats
    assert scores["relevance_score"] == 100.0 # in required_pids
    assert scores["cost_score"] == 100.0 - (120.0 / 5.0)

def test_calculate_cart_capability_coverage():
    service = CapabilityIntelligenceService()
    
    products = [
        {
            "title": "Organic Rolled Oats 1kg",
            "subcategory": "Breakfast Oats",
            "category_path": ["Grocery", "Breakfast"],
            "semanticTags": ["organic", "whole grain", "fiber"]
        },
        {
            "title": "Whey Protein Bar",
            "subcategory": "Snacks",
            "category_path": ["Grocery", "Snacks"],
            "semanticTags": ["protein", "high protein"]
        }
    ]
    
    req_caps = ["protein_intake", "fiber_intake", "calorie_control", "satiety", "hydration"]
    
    coverage = service.calculate_cart_capability_coverage(products, req_caps)
    # Oats covers: fiber_intake, satiety. Protein Bar covers: protein_intake, satiety.
    # Total covered: protein_intake, fiber_intake, satiety. 3 out of 5 = 60%.
    assert coverage == 60

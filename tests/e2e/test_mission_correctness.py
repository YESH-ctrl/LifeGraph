import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from graph.service import GraphService
from shared.repositories.product_repository import ProductRepository

def test_mission_correctness():
    gs = GraphService()
    product_repo = ProductRepository()
    
    # 1. Cooking missions must never return: Beauty, Cleaning, Baby Care
    cooking_missions = ["chicken_biryani", "family_breakfast_setup", "weekend_cooking_session", "paneer_butter_masala_dinner"]
    invalid_cooking_cats = ["BEAUTY_&_HYGIENE", "CLEANING_&_HOUSEHOLD", "BABY_CARE"]
    
    for mission_id in cooking_missions:
        reqs = gs.get_mission_requirements(mission_id)
        for req in reqs:
            product = product_repo.get_product(req)
            if product:
                cat = (product.category or "").upper()
                assert cat not in invalid_cooking_cats, f"Cooking mission {mission_id} contains invalid category {cat} via product {product.title}"

    # 4. Chicken Biryani must contain food products only
    cb_reqs = gs.get_mission_requirements("chicken_biryani")
    for req in cb_reqs:
        product = product_repo.get_product(req)
        if product:
            cat = (product.category or "").upper()
            assert cat in ["FOODGRAINS_OIL_&_MASALA", "BAKERY_CAKES_&_DAIRY", "SNACKS_&_BRANDED_FOODS", "BEVERAGES", "GOURMET_&_WORLD_FOOD", "FRUITS_&_VEGETABLES", "EGGS_MEAT_&_FISH", "FOOD", "GROCERY", "GROCERY_&_GOURMET_FOODS"], f"Chicken Biryani contains non-food product: {product.title} (Category: {cat})"

    # 5. Movie Night must contain snack/beverage products only
    mn_reqs = gs.get_mission_requirements("movie_night")
    for req in mn_reqs:
        product = product_repo.get_product(req)
        if product:
            cat = (product.category or "").upper()
            assert cat in ["SNACKS_&_BRANDED_FOODS", "BEVERAGES", "BAKERY_CAKES_&_DAIRY", "GROCERY", "GROCERY_&_GOURMET_FOODS"], f"Movie Night contains non-snack/beverage product: {product.title} (Category: {cat})"

    # 6. House Party must contain snack/beverage/party products only
    hp_reqs = gs.get_mission_requirements("house_party")
    for req in hp_reqs:
        product = product_repo.get_product(req)
        if product:
            cat = (product.category or "").upper()
            assert cat in ["SNACKS_&_BRANDED_FOODS", "BEVERAGES", "BAKERY_CAKES_&_DAIRY", "CLEANING_&_HOUSEHOLD", "GROCERY", "GROCERY_&_GOURMET_FOODS"], f"House Party contains invalid product: {product.title} (Category: {cat})"

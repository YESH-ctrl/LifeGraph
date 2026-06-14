import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from graph.service import GraphService
from shared.repositories.product_repository import ProductRepository

# 7. Explicit absurdity tests: Shampoo in cooking, Toothpaste in movie night, Diapers in house party.
def test_explicit_absurdity():
    gs = GraphService()
    product_repo = ProductRepository()
    
    # 1. Shampoo in cooking missions
    cooking_missions = ["chicken_biryani", "family_breakfast_setup", "weekend_cooking_session", "paneer_butter_masala_dinner"]
    for mission_id in cooking_missions:
        reqs = gs.get_mission_requirements(mission_id)
        for req in reqs:
            product = product_repo.get_product(req)
            if product:
                assert "shampoo" not in product.title.lower(), f"Absurdity: Shampoo found in cooking mission {mission_id}: {product.title}"
                
    # 2. Toothpaste in movie night
    mn_reqs = gs.get_mission_requirements("movie_night")
    for req in mn_reqs:
        product = product_repo.get_product(req)
        if product:
            assert "toothpaste" not in product.title.lower(), f"Absurdity: Toothpaste found in movie_night: {product.title}"
            
    # 3. Diapers in house party
    hp_reqs = gs.get_mission_requirements("house_party")
    for req in hp_reqs:
        product = product_repo.get_product(req)
        if product:
            assert "diaper" not in product.title.lower(), f"Absurdity: Diapers found in house_party: {product.title}"

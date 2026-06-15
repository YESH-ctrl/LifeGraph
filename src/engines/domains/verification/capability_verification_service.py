import logging
from typing import Dict, List, Any, Set
from foundation.graph.repository import GraphRepository
from engines.domains.capability_intelligence_service import CapabilityIntelligenceService
from engines.domains.category_guard import display_title_resolution, check_mismatch
from engines.domains.product_diversity_engine import ProductDiversityEngine

logger = logging.getLogger(__name__)

class CapabilityVerificationService:
    def __init__(self):
        self.graph_repo = GraphRepository()
        self.capability_service = CapabilityIntelligenceService()
        self.diversity_engine = ProductDiversityEngine()

    def get_product_groups(self, product: Dict[str, Any]) -> List[str]:
        """Classifies a product into outcome blueprint groups based on title, subcategory, and tags."""
        title = (product.get("title") or product.get("name") or "").lower()
        subcat = (product.get("subcategory") or "").lower()
        tags = [str(t).lower() for t in product.get("semanticTags", [])]
        combined = f"{title} {subcat} {' '.join(tags)}".replace("_", " ")

        def matches_any(keywords: List[str]) -> bool:
            return any(kw in combined for kw in keywords)

        groups = []
        
        # 1. Weight Loss Groups
        if matches_any(["protein", "whey", "egg", "almond", "paneer", "tofu", "milk", "dal", "lentils", "chicken", "fish", "meat", "peanut", "seeds"]):
            groups.append("protein_source")
        if matches_any(["oat", "fiber", "chia", "seeds", "quinoa", "dry fruits", "dates", "muesli", "granola"]):
            groups.append("fiber_source")
        if matches_any(["almond", "nuts", "seeds", "chia", "olive oil", "ghee", "fish", "avocado", "flax", "oil"]):
            groups.append("healthy_fat")
        if matches_any(["water", "drink", "tea", "green tea", "coconut", "juice", "beverage", "milk"]):
            groups.append("hydration")
        if matches_any(["oats", "muesli", "granola", "bread", "eggs", "flakes", "cereal", "cookies", "biscuit"]):
            groups.append("breakfast_option")
            
        # 2. Healthy Eating Groups
        if matches_any(["oats", "muesli", "milk", "eggs", "paneer", "atta", "oil", "rice", "dal", "lentils", "ghee", "butter", "cheese"]):
            groups.append("balanced_macros")
        if matches_any(["organic", "oats", "quinoa", "honey", "seeds", "chia", "nuts", "almonds", "dry fruits", "rice", "dal", "lentils", "whole wheat", "whole grains"]):
            groups.append("whole_foods")
        if matches_any(["honey", "seeds", "chia", "almond", "dry fruits", "green tea", "vitamins", "minerals", "saffron", "cashew", "walnut"]):
            groups.append("micronutrients")
        if matches_any(["bar", "cookies", "snack", "popcorn", "digestive", "chocolate", "namkeen", "chips"]):
            groups.append("healthy_snacks")
            
        # 3. Monthly Refill Groups
        if matches_any(["rice", "atta", "oil", "ghee", "dal", "salt", "sugar", "milk", "wheat", "flour"]):
            groups.append("staples")
        if matches_any(["cleaning", "wash", "soap", "detergent", "shampoo", "toothpaste", "toilet", "scrub", "liquid detergent", "washing powder", "wipe", "tissue"]):
            groups.append("household_consumables")
        if matches_any(["bread", "paneer", "curd", "eggs", "masala", "spice", "tea", "coffee", "butter", "cheese", "spread"]):
            groups.append("meal_ingredients")
            
        return groups

    def verify_capabilities(
        self,
        mission_id: str,
        capabilities: List[str],
        cart_products: List[Dict[str, Any]],
        blueprint: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dynamically verifies cart products against required capabilities, blueprint groups, and diversity.
        """
        # 1. Capability Completion
        covered_caps = set()
        for prod in cart_products:
            for cap in capabilities:
                if self.capability_service.check_product_capability_coverage(prod, cap):
                    covered_caps.add(cap)
                    
        cap_completion = int(len(covered_caps) / len(capabilities) * 100) if capabilities else 100
        missing_caps = [c for c in capabilities if c not in covered_caps]

        # 2. Group Completion
        required_groups = blueprint.get("required_groups", [])
        covered_groups = set()
        for prod in cart_products:
            prod_groups = self.get_product_groups(prod)
            for g in prod_groups:
                if g in required_groups:
                    covered_groups.add(g)
                    
        group_completion = int(len(covered_groups) / len(required_groups) * 100) if required_groups else 100
        missing_groups = [g for g in required_groups if g not in covered_groups]

        # 3. Dynamic Recommended Additions
        recommended_additions = []
        if missing_caps or missing_groups:
            # Gather candidates from graph db
            try:
                db_items = self.graph_repo.table.scan().get("Items", [])
            except Exception:
                db_items = []
                
            seen_pids = {p.get("product_id") or p.get("id") for p in cart_products}
            
            for item in db_items:
                pk = item.get("PK", "")
                sk = item.get("SK", "")
                if pk.startswith("PRODUCT#") and sk == "METADATA":
                    pid = pk.split("#")[1]
                    if pid not in seen_pids:
                        title = display_title_resolution(pid, item)
                        if title:
                            prod_info = dict(item)
                            prod_info["title"] = title
                            prod_info["id"] = pid
                            mismatch, _ = check_mismatch(mission_id, prod_info)
                            if not mismatch:
                                # Check if it covers missing cap or group
                                prod_caps = self.capability_service.get_product_capabilities(prod_info, missing_caps)
                                prod_groups = self.get_product_groups(prod_info)
                                covers_missing_group = any(g in missing_groups for g in prod_groups)
                                
                                if prod_caps or covers_missing_group:
                                    recommended_additions.append(pid)
                                    if len(recommended_additions) >= 5:
                                        break
                                        
        return {
            "capability_completion": cap_completion,
            "group_completion": group_completion,
            "missing_capabilities": missing_caps,
            "missing_groups": missing_groups,
            "recommended_additions": recommended_additions
        }

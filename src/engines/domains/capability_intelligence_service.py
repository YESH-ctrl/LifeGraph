import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Mission to Capabilities mapping (Task 2)
MISSION_TO_CAPABILITIES = {
    "weight_loss_journey": ["protein_intake", "fiber_intake", "calorie_control", "satiety", "hydration"],
    "healthy_lifestyle_start": ["balanced_macros", "micronutrients", "whole_foods"],
    "weekly_grocery_shopping": ["staple_coverage", "meal_variety", "cost_efficiency"],
    "monthly_grocery_refill": ["pantry_refill", "household_consumables", "repeat_purchase_items"],
    "chicken_biryani": ["staple_coverage", "meal_variety", "cost_efficiency"],
    "weekend_cooking_session": ["staple_coverage", "meal_variety", "cost_efficiency"],
    "general_refill": ["pantry_refill", "household_consumables", "repeat_purchase_items"]
}

class CapabilityIntelligenceService:
    def __init__(self):
        pass

    def get_capabilities_for_mission(self, mission_id: str) -> List[str]:
        """Returns the capabilities required for a given mission."""
        return MISSION_TO_CAPABILITIES.get(mission_id, ["staple_coverage", "meal_variety", "cost_efficiency"])

    def check_product_capability_coverage(self, product: Dict[str, Any], capability: str) -> bool:
        """
        Determines if a product satisfies a given capability.
        Evaluates title, subcategory, category path, and semantic tags.
        """
        title = (product.get("title") or product.get("name") or "").lower()
        subcat = (product.get("subcategory") or "").lower()
        
        category_path = product.get("category_path") or []
        if isinstance(category_path, list):
            category = " ".join(category_path).lower()
        else:
            category = str(category_path).lower()
            
        tags = [str(t).lower() for t in product.get("semanticTags", [])]
        
        # Combine fields for holistic matching
        combined = f"{title} {subcat} {category} {' '.join(tags)}".replace("_", " ")

        def matches_any(keywords: List[str]) -> bool:
            return any(kw in combined for kw in keywords)

        # Mapping rules from capabilities to product attributes
        if capability == "protein_intake":
            return matches_any(["protein", "whey", "egg", "almond", "paneer", "tofu", "milk", "dal", "lentils", "seeds", "nuts", "chicken", "fish", "meat", "peanut", "cashew"])
        elif capability == "fiber_intake":
            return matches_any(["oat", "fiber", "chia", "seeds", "quinoa", "dry fruits", "almonds", "dates", "bran", "muesli", "granola"])
        elif capability == "calorie_control":
            return matches_any(["green tea", "low calorie", "low sugar", "stevia", "diet", "water", "honey", "unsweetened", "sugar free", "sugar_free", "zero calorie"])
        elif capability == "satiety":
            return matches_any(["oats", "seeds", "paneer", "muesli", "atta", "wheat", "rice", "dal", "lentils", "quinoa", "bar", "protein"])
        elif capability == "hydration":
            return matches_any(["water", "drink", "tea", "green tea", "coconut", "juice", "beverage", "milk", "soda", "liquid"])
        elif capability == "balanced_macros":
            return matches_any(["oats", "muesli", "milk", "eggs", "paneer", "atta", "oil", "rice", "dal", "lentils", "ghee", "butter", "cheese"])
        elif capability == "micronutrients":
            return matches_any(["honey", "seeds", "chia", "almond", "dry fruits", "green tea", "vitamins", "minerals", "saffron", "cashew", "walnut"])
        elif capability == "whole_foods":
            return matches_any(["organic", "oats", "quinoa", "honey", "seeds", "chia", "nuts", "almonds", "dry fruits", "rice", "dal", "lentils", "whole wheat", "whole grains"])
        elif capability == "staple_coverage":
            return matches_any(["rice", "atta", "oil", "ghee", "dal", "salt", "sugar", "milk", "wheat", "flour", "staple"])
        elif capability == "meal_variety":
            return matches_any(["bread", "paneer", "curd", "eggs", "masala", "spice", "tea", "coffee", "yoghurt", "sauce", "ketchup", "butter", "cheese", "spread"])
        elif capability == "cost_efficiency":
            price = float(product.get("price", 0.0))
            return price < 150.0 or matches_any(["budget", "value", "economical", "pack", "discount", "free"])
        elif capability == "pantry_refill":
            return matches_any(["rice", "atta", "oil", "dal", "salt", "sugar", "tea", "coffee", "flour", "ghee", "masala", "spice", "pantry"])
        elif capability == "household_consumables":
            return matches_any(["cleaning", "wash", "soap", "detergent", "shampoo", "toothpaste", "toilet", "scrub", "cleaner", "liquid detergent", "washing powder", "wipe", "tissue"])
        elif capability == "repeat_purchase_items":
            return matches_any(["milk", "bread", "eggs", "curd", "butter", "cheese", "yogurt", "yoghurt", "paneer", "daily", "fresh"])
            
        return False

    def get_product_capabilities(self, product: Dict[str, Any], mission_capabilities: List[str]) -> List[str]:
        """Returns the list of capabilities covered by this product for a specific mission."""
        return [cap for cap in mission_capabilities if self.check_product_capability_coverage(product, cap)]

    def score_product(self, product: Dict[str, Any], mission_id: str, required_pids: set, optional_pids: set) -> Dict[str, Any]:
        """
        Computes the 4-part weighted score for a product:
        - 40% Capability Coverage
        - 30% Nutritional Quality
        - 20% Mission Relevance
        - 10% Cost Efficiency
        """
        capabilities = self.get_capabilities_for_mission(mission_id)
        
        # 1. Capability Coverage Score (40%)
        covered = self.get_product_capabilities(product, capabilities)
        capability_score = (len(covered) / len(capabilities) * 100.0) if capabilities else 100.0
        
        # 2. Nutritional Quality Score (30%)
        nutrition_score = self.calculate_nutritional_quality(product)
        
        # 3. Mission Relevance Score (20%)
        relevance_score = self.calculate_mission_relevance(product, mission_id, required_pids, optional_pids)
        
        # 4. Cost Efficiency Score (10%)
        cost_score = self.calculate_cost_efficiency(product)
        
        # Aggregate final score
        final_score = (
            0.40 * capability_score +
            0.30 * nutrition_score +
            0.20 * relevance_score +
            0.10 * cost_score
        )
        
        return {
            "final_score": final_score,
            "capability_score": capability_score,
            "nutrition_score": nutrition_score,
            "relevance_score": relevance_score,
            "cost_score": cost_score,
            "covered_capabilities": covered
        }

    def calculate_nutritional_quality(self, product: Dict[str, Any]) -> float:
        title = (product.get("title") or product.get("name") or "").lower()
        subcat = (product.get("subcategory") or "").lower()
        tags = [str(t).lower() for t in product.get("semanticTags", [])]
        combined = f"{title} {subcat} {' '.join(tags)}".replace("_", " ")
        
        # High quality healthy items
        if any(kw in combined for kw in ["organic", "whole grain", "oats", "quinoa", "chia", "seeds", "nuts", "almond", "honey", "green tea", "sugar free", "diet", "raw"]):
            return 95.0
        # Standard healthy foods
        if any(kw in combined for kw in ["rice", "atta", "wheat", "dal", "lentils", "milk", "curd", "paneer", "eggs", "oil", "ghee", "salt", "sugar"]):
            return 80.0
        # Processed or lower nutritional quality foods / cleaning items
        if any(kw in combined for kw in ["chocolate", "biscuit", "cookie", "chips", "snack", "namkeen", "cleaning", "soap", "detergent", "shampoo", "toothpaste"]):
            return 50.0
            
        return 70.0

    def calculate_mission_relevance(self, product: Dict[str, Any], mission_id: str, required_pids: set, optional_pids: set) -> float:
        pid = product.get("id") or product.get("product_id")
        relevance = 40.0
        
        if pid in required_pids:
            relevance = 100.0
        elif pid in optional_pids:
            relevance = 80.0
            
        prim = str(product.get("primary_missions", [])).lower()
        sec = str(product.get("secondary_missions", [])).lower()
        hints = str(product.get("missionHints", [])).lower()
        m_lower = mission_id.lower()
        
        if m_lower in prim or m_lower in sec:
            relevance = max(relevance, 90.0)
        elif m_lower in hints:
            relevance = max(relevance, 70.0)
            
        return relevance

    def calculate_cost_efficiency(self, product: Dict[str, Any]) -> float:
        price = float(product.get("price", 0.0))
        # Price 0 -> 100 score, price 500+ -> 10 score
        efficiency = 100.0 - (price / 5.0)
        return max(10.0, min(100.0, efficiency))

    def calculate_cart_capability_coverage(self, selected_products: List[Dict[str, Any]], required_capabilities: List[str]) -> int:
        """Calculates percentage of required capabilities covered by the cart products."""
        if not required_capabilities:
            return 100
            
        covered_set = set()
        for prod in selected_products:
            for cap in required_capabilities:
                if self.check_product_capability_coverage(prod, cap):
                    covered_set.add(cap)
                    
        return int(len(covered_set) / len(required_capabilities) * 100)

from typing import List, Dict, Any

class ProductDiversityEngine:
    def calculate_diversity_score(self, cart_products: List[Dict[str, Any]]) -> float:
        """
        Calculates the diversity score of the cart based on subcategory uniqueness.
        diversity_score = (unique_subcategories / total_items) * 100.
        If empty, returns 100.0.
        """
        if not cart_products:
            return 100.0
            
        subcategories = []
        for i, prod in enumerate(cart_products):
            sub = prod.get("subcategory") or prod.get("sub_category") or ""
            if not sub:
                # Fallback to category path or unique identifier if subcategory is missing
                cat_path = prod.get("category_path")
                if isinstance(cat_path, list) and cat_path:
                    sub = cat_path[-1]
                else:
                    sub = f"unknown_subcat_{i}"
            subcategories.append(sub.strip().lower())
            
        unique_subs = set(subcategories)
        score = (len(unique_subs) / len(cart_products)) * 100.0
        return min(100.0, max(0.0, score))

    def filter_diverse_products(self, candidates: List[Dict[str, Any]], target_count: int = 8) -> List[Dict[str, Any]]:
        """
        Deduplicates candidate products by subcategory to enforce diversity.
        Permits max one product per subcategory.
        """
        selected = []
        seen_subcats = set()
        
        # Pass 1: Add at most one product per unique subcategory
        for c in candidates:
            prod_info = c.get("prod_info") or c
            sub = (prod_info.get("subcategory") or "").strip().lower()
            if sub and sub not in seen_subcats:
                selected.append(c)
                seen_subcats.add(sub)
                
        # Pass 2: If we need more items to satisfy size, select remaining top items
        if len(selected) < target_count:
            selected_ids = {p.get("product_id") or p.get("id") for p in selected}
            for c in candidates:
                pid = c.get("product_id") or c.get("id")
                if pid not in selected_ids:
                    selected.append(c)
                    selected_ids.add(pid)
                    if len(selected) >= target_count:
                        break
                        
        return selected

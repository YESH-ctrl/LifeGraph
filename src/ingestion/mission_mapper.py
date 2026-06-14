from typing import List, Dict, Any

def map_products_to_mission(products: List[Dict[str, Any]], mission_template: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Selects products for a mission based on categories, subcategories, semantic tags, and mission hints.
    Returns:
        {
            "required": List of product_ids,
            "optional": List of product_ids
        }
    """
    mapping_rules = mission_template.get("mapping_rules", {})
    req_rules = mapping_rules.get("required", {})
    opt_rules = mapping_rules.get("optional", {})

    req_categories = [c.lower() for c in req_rules.get("categories", [])]
    req_subcategories = [s.lower() for s in req_rules.get("subcategories", [])]
    req_tags = [t.lower() for t in req_rules.get("semantic_tags", [])]
    req_hints = [h.lower() for h in req_rules.get("mission_hints", [])]

    opt_categories = [c.lower() for c in opt_rules.get("categories", [])]
    opt_subcategories = [s.lower() for s in opt_rules.get("subcategories", [])]
    opt_tags = [t.lower() for t in opt_rules.get("semantic_tags", [])]
    opt_hints = [h.lower() for h in opt_rules.get("mission_hints", [])]

    required_product_ids = []
    optional_product_ids = []

    for product in products:
        p_id = product["id"]
        cat = product["category"].lower()
        subcat = product["subcategory"].lower()
        tags = [t.lower() for t in product.get("semanticTags", [])]
        hints = [h.lower() for h in product.get("missionHints", [])]

        # Check required rules
        is_required = False
        if cat in req_categories:
            is_required = True
        elif subcat in req_subcategories:
            is_required = True
        elif any(t in req_tags for t in tags):
            is_required = True
        elif any(h in req_hints for h in hints):
            is_required = True

        if is_required:
            required_product_ids.append(p_id)
            continue

        # Check optional rules
        is_optional = False
        if cat in opt_categories:
            is_optional = True
        elif subcat in opt_subcategories:
            is_optional = True
        elif any(t in opt_tags for t in tags):
            is_optional = True
        elif any(h in opt_hints for h in hints):
            is_optional = True

        if is_optional:
            optional_product_ids.append(p_id)

    return {
        "required": required_product_ids,
        "optional": optional_product_ids
    }

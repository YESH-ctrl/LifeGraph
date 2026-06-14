from typing import List, Dict, Any
from decimal import Decimal

def generate_relationships(
    mission_id: str,
    required_ids: List[str],
    optional_ids: List[str],
    template_relationships: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generates DynamoDB items for mission-product and product-product relationships.
    """
    items = []

    # 1. Mission -> Product (Required)
    for idx, p_id in enumerate(required_ids):
        # Deterministic weights and priority matching legacy seeder
        priority = "CRITICAL" if idx < 2 else "IMPORTANT"
        weight = 40 if idx == 0 else (20 if idx == 1 else 10)
        items.append({
            "PK": f"MISSION#{mission_id}",
            "SK": f"REQUIRES#PRODUCT#{p_id}",
            "sourceType": "MISSION",
            "sourceId": mission_id,
            "targetType": "PRODUCT",
            "targetId": p_id,
            "relationshipType": "REQUIRES",
            "priority": priority,
            "weight": weight
        })

        # Product INDICATES Mission (back-edge)
        strength = 0.95 if idx < 2 else 0.75
        items.append({
            "PK": f"PRODUCT#{p_id}",
            "SK": f"INDICATES#MISSION#{mission_id}",
            "strength": Decimal(str(strength))
        })

    # 2. Mission -> Product (Optional)
    for p_id in optional_ids:
        items.append({
            "PK": f"MISSION#{mission_id}",
            "SK": f"OPTIONAL#PRODUCT#{p_id}",
            "sourceType": "MISSION",
            "sourceId": mission_id,
            "targetType": "PRODUCT",
            "targetId": p_id,
            "relationshipType": "OPTIONAL",
            "priority": "OPTIONAL",
            "weight": 2
        })

    # Helper set of all products in this mission (both required and optional)
    all_mapped_products = set(required_ids + optional_ids)

    # 3. Product -> Product relationships
    # ONLY generate product-product relationships if BOTH products are in the imported set/mapped products
    for dep in template_relationships.get("dependencies", []):
        src, tgt = dep["source"], dep["target"]
        if src in all_mapped_products and tgt in all_mapped_products:
            items.append({
                "PK": f"PRODUCT#{src}",
                "SK": f"DEPENDS_ON#PRODUCT#{tgt}",
                "sourceType": "PRODUCT",
                "sourceId": src,
                "targetType": "PRODUCT",
                "targetId": tgt,
                "relationshipType": "DEPENDS_ON"
            })

    for comp in template_relationships.get("compatibility", []):
        src, tgt = comp["source"], comp["target"]
        if src in all_mapped_products and tgt in all_mapped_products:
            items.append({
                "PK": f"PRODUCT#{src}",
                "SK": f"COMPATIBLE_WITH#PRODUCT#{tgt}",
                "sourceType": "PRODUCT",
                "sourceId": src,
                "targetType": "PRODUCT",
                "targetId": tgt,
                "relationshipType": "COMPATIBLE_WITH"
            })

    for sub in template_relationships.get("substitutions", []):
        src, tgt = sub["source"], sub["target"]
        if src in all_mapped_products and tgt in all_mapped_products:
            items.append({
                "PK": f"PRODUCT#{src}",
                "SK": f"SUBSTITUTES_FOR#PRODUCT#{tgt}",
                "sourceType": "PRODUCT",
                "sourceId": src,
                "targetType": "PRODUCT",
                "targetId": tgt,
                "relationshipType": "SUBSTITUTES_FOR"
            })

    return items

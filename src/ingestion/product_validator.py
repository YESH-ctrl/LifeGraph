from typing import Tuple, Dict, Any

IMPOSSIBLE_COMBINATIONS = {
    "colgate": ["backpack", "bag", "luggage", "garland", "balloon", "party", "toy"],
    "dettol": ["garland", "flower", "gift", "balloon", "party", "toy", "backpack", "bag", "decor"],
    "godrej": ["balloon", "party", "garland", "toy"]
}

def validate_product(product: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates a transformed product dictionary.
    Returns (True, "") if valid, or (False, "Reason") if invalid.
    """
    title = product.get("title")
    if not title or not str(title).strip():
        return False, "Missing title"

    category = product.get("category")
    if not category or not str(category).strip():
        return False, "Missing category"

    # Price validation
    price = product.get("price")
    try:
        price_val = float(price) if price is not None else -1.0
        if price_val < 0:
            return False, f"Invalid price: {price}"
    except (ValueError, TypeError):
        return False, f"Invalid price: {price}"

    # Rating validation
    rating = product.get("rating")
    try:
        rating_val = float(rating) if rating is not None else -1.0
        if rating_val < 0 or rating_val > 5:
            return False, f"Invalid rating: {rating}"
    except (ValueError, TypeError):
        return False, f"Invalid rating: {rating}"

    # Review count validation
    reviews = product.get("reviews")
    try:
        reviews_val = int(reviews) if reviews is not None else -1
        if reviews_val < 0:
            return False, f"Invalid review count: {reviews}"
    except (ValueError, TypeError):
        return False, f"Invalid review count: {reviews}"

    # Impossible brand-category combinations validation
    brand = str(product.get("brand") or "").strip().lower()
    subcat = str(product.get("subcategory") or "").strip().lower()
    cat_lower = str(category).strip().lower()
    title_lower = str(title).strip().lower()

    for forbidden_brand, forbidden_keywords in IMPOSSIBLE_COMBINATIONS.items():
        if forbidden_brand in brand:
            for kw in forbidden_keywords:
                if kw in cat_lower or kw in subcat or kw in title_lower:
                    return False, f"Impossible brand-category combination: Brand '{product.get('brand')}' with '{kw}' related product/category"

    return True, ""

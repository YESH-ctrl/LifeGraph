import re
from typing import Dict, Any, List

def slugify(text: str) -> str:
    """Converts text into a deterministic, slugified product ID."""
    text = str(text or "").lower().strip()
    # Replace non-alphanumeric with underscores
    text = re.sub(r'[^a-z0-9]+', '_', text)
    # Collapse multiple underscores
    text = re.sub(r'_+', '_', text)
    # Strip leading/trailing underscores
    text = text.strip('_')
    return text

def transform_row_to_product(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms a raw row (dict) into the standard LifeGraph Product Schema.
    """
    # Normalize keys of raw row (strip whitespace, lowercase, remove underscores)
    normalized_row = {}
    for k, v in row.items():
        norm_k = str(k).strip().lower().replace("_", "").replace(" ", "")
        normalized_row[norm_k] = v

    # Helper to retrieve value by list of possible normalized keys
    def get_val(possible_keys, default=None):
        for pk in possible_keys:
            if pk in normalized_row:
                return normalized_row[pk]
        return default

    # Extract raw fields
    title = get_val(["title", "name", "productname", "producttitle"], "")
    
    brand = get_val(["brand", "brandname", "productbrand"], None)
    if not brand or str(brand).strip().lower() == "generic":
        # Extract first word of title as brand
        words = str(title).strip().split()
        if words:
            first_word = re.sub(r'[^a-zA-Z0-9]+', '', words[0])
            brand = first_word.capitalize() if first_word else "Generic"
        else:
            brand = "Generic"

    category = get_val(["category", "maincategory", "productcategory"], "")
    subcategory = get_val(["subcategory", "subcategory", "productsubcategory"], "")
    description = get_val(["description", "productdescription"], "")
    
    price_raw = get_val(["price", "discountprice", "productprice", "sellingprice"], 0)
    mrp_raw = get_val(["mrp", "actualprice", "mrpval", "maximumretailprice"], None)
    rating_raw = get_val(["rating", "ratings", "productrating", "average_rating"], 0)
    reviews_raw = get_val(["reviews", "noofratings", "reviewcount", "numberofreviews"], 0)
    
    image = get_val(["image", "imageurl", "productimage", "img"], "")
    stock_raw = get_val(["stock", "quantity", "stockcount"], 100)
    prime_raw = get_val(["prime", "isprime", "amazonprime"], True)
    delivery_days_raw = get_val(["deliverydays", "deliverytime"], 1)
    
    # Helper to clean currency symbols, commas, and quotes from numeric strings
    def clean_numeric_str(val):
        if val is None or val == "":
            return None
        s = str(val).strip()
        s = s.replace("₹", "").replace(",", "").replace('"', '').replace("'", "")
        return s.strip()

    # Clean price/mrp
    price_str = clean_numeric_str(price_raw)
    try:
        price = float(price_str) if price_str is not None else 0.0
    except (ValueError, TypeError):
        price = 0.0

    mrp_str = clean_numeric_str(mrp_raw)
    try:
        mrp = float(mrp_str) if mrp_str is not None else price
    except (ValueError, TypeError):
        mrp = price

    # Clean rating/reviews/stock
    rating_str = clean_numeric_str(rating_raw)
    try:
        rating = float(rating_str) if rating_str is not None else 0.0
    except (ValueError, TypeError):
        rating = 0.0

    reviews_str = clean_numeric_str(reviews_raw)
    try:
        reviews = int(reviews_str) if reviews_str is not None else 0
    except (ValueError, TypeError):
        reviews = 0

    stock_str = clean_numeric_str(stock_raw)
    try:
        stock = int(stock_str) if stock_str is not None else 100
    except (ValueError, TypeError):
        stock = 100

    # Clean prime
    if isinstance(prime_raw, str):
        prime = prime_raw.lower() in ("true", "yes", "1", "y")
    else:
        prime = bool(prime_raw)

    # Clean delivery days
    delivery_days_str = clean_numeric_str(delivery_days_raw)
    try:
        delivery_days = int(delivery_days_str) if delivery_days_str is not None else 1
    except (ValueError, TypeError):
        delivery_days = 1

    # Semantic tags and mission hints parsing (handle strings or lists)
    def parse_list(val):
        if val is None or val == "":
            return []
        if isinstance(val, list):
            return [str(x).strip() for x in val if x]
        if isinstance(val, str):
            return [str(x).strip() for x in val.split(",") if x.strip()]
        return [str(val).strip()]

    raw_tags = parse_list(get_val(["semantictags", "tags"]))
    raw_hints = parse_list(get_val(["missionhints", "hints"]))

    # Normalize category and enrich with intelligence layer rules
    from data_ingestion.product_intelligence import enrich_product_metadata, APPROVED_MISSIONS
    intel = enrich_product_metadata(title, category)
    
    category = intel["category"]
    subcategory = intel["subcategory"]
    
    # Merge custom tags and hints
    semantic_tags = []
    for t in raw_tags:
        t_clean = t.lower().strip()
        if t_clean and t_clean not in semantic_tags:
            semantic_tags.append(t_clean)
    for t in intel["semanticTags"]:
        t_clean = t.lower().strip()
        if t_clean and t_clean not in semantic_tags:
            semantic_tags.append(t_clean)
            
    mission_hints = []
    # add from raw hints with a default score if they are valid
    for h in raw_hints:
        h_clean = h.lower().strip()
        if h_clean in APPROVED_MISSIONS:
            # check if already added
            if not any(mh["mission"] == h_clean for mh in mission_hints):
                mission_hints.append({"mission": h_clean, "score": 0.5})
                
    # add from intel
    for h in intel["missionHints"]:
        h_mission = h["mission"]
        if h_mission in APPROVED_MISSIONS:
            existing = next((mh for mh in mission_hints if mh["mission"] == h_mission), None)
            if existing:
                existing["score"] = max(existing["score"], h["score"])
            else:
                mission_hints.append(h)

    # Convert score to Decimal for DynamoDB
    from decimal import Decimal
    for mh in mission_hints:
        mh["score"] = Decimal(str(mh["score"]))

    # Use the natural language embedding text from product intelligence
    embedding_text = intel["embeddingText"]

    product_id = slugify(title)

    product_schema = {
        "PK": f"PRODUCT#{product_id}",
        "SK": "METADATA",
        "entityType": "PRODUCT",
        "id": product_id,
        "name": str(title).strip(),
        "title": str(title).strip(),
        "brand": str(brand).strip(),
        "category": str(category).strip(),
        "subcategory": str(subcategory).strip(),
        "description": str(description).strip(),
        "price": price,
        "mrp": mrp,
        "rating": rating,
        "reviews": reviews,
        "image": str(image).strip(),
        "stock": stock,
        "prime": prime,
        "deliveryDays": delivery_days,
        "semanticTags": semantic_tags,
        "missionHints": mission_hints,
        "embeddingText": embedding_text,
        "GSI1PK": f"CATEGORY#{str(category).strip()}",
        "GSI1SK": f"PRODUCT#{product_id}"
    }

    return product_schema

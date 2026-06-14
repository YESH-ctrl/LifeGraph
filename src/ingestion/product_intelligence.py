import re
from typing import Dict, Any, List

# Approved 20 missions
APPROVED_MISSIONS = {
    "monthly_grocery_refill": "Monthly Grocery Refill",
    "weekly_grocery_shopping": "Weekly Grocery Shopping",
    "family_breakfast_setup": "Family Breakfast Setup",
    "biryani_preparation": "Biryani Preparation",
    "weekend_cooking_session": "Weekend Cooking Session",
    "paneer_butter_masala_dinner": "Paneer Butter Masala Dinner",
    "diwali_celebration": "Diwali Celebration",
    "ganesh_chaturthi_preparation": "Ganesh Chaturthi Preparation",
    "sankranti_preparation": "Sankranti Preparation",
    "birthday_party": "Birthday Party",
    "housewarming_ceremony": "Housewarming Ceremony",
    "new_semester_setup": "New Semester Setup",
    "hostel_essentials_refill": "Hostel Essentials Refill",
    "exam_preparation_week": "Exam Preparation Week",
    "train_journey_snacks": "Train Journey Snacks",
    "road_trip_essentials": "Road Trip Essentials",
    "healthy_lifestyle_start": "Healthy Lifestyle Start",
    "weight_loss_journey": "Weight Loss Journey",
    "elderly_care_essentials": "Elderly Care Essentials",
    "family_gathering": "Family Gathering"
}

def score_missions(title: str, category: str, subcategory: str, semanticTags: List[str]) -> List[Dict[str, Any]]:
    """
    Scores relevance of the 20 approved missions based on product attributes.
    Returns a list of dicts: [{"mission": "...", "score": 0.85}, ...]
    """
    title_lower = str(title).lower()
    cat_lower = str(category).lower()
    subcat_lower = str(subcategory).lower()
    tags_str = " ".join(semanticTags).lower()
    
    scored_hints = []
    
    for mission_key, mission_name in APPROVED_MISSIONS.items():
        score = 0.0
        mission_lower = mission_name.lower().replace("_", " ")
        mission_parts = mission_lower.split()
        
        # Base relevance from explicit rule assignment matches (passed in as subcategory/tags implicitly, handled via heuristics)
        
        # 1. Category relevance
        if "grocery" in cat_lower and "grocery" in mission_lower:
            score += 0.3
        if "festival" in cat_lower and ("celebration" in mission_lower or "chaturthi" in mission_lower or "sankranti" in mission_lower):
            score += 0.4
        
        # 2. Semantic Tag relevance
        for tag in semanticTags:
            tag_lower = tag.lower()
            if tag_lower in mission_lower:
                score += 0.4
            # specific mapping heuristics
            if tag_lower == "breakfast" and "breakfast" in mission_lower:
                score += 0.5
            if tag_lower in ["snack", "munchies"] and "snacks" in mission_lower:
                score += 0.5
            if tag_lower in ["health", "fitness", "wellness"] and ("healthy" in mission_lower or "weight" in mission_lower):
                score += 0.5
            if tag_lower == "elderly care" and "elderly" in mission_lower:
                score += 0.6
                
        # 3. Subcategory relevance
        if "party" in subcat_lower and "party" in mission_lower:
            score += 0.4
        if "pooja" in subcat_lower and ("celebration" in mission_lower or "chaturthi" in mission_lower or "sankranti" in mission_lower):
            score += 0.4
            
        # 4. Title keywords relevance
        title_keywords = set(re.findall(r'\w+', title_lower))
        mission_keywords = set(re.findall(r'\w+', mission_lower))
        
        overlap = title_keywords.intersection(mission_keywords)
        if overlap:
            score += 0.2 * len(overlap)
            
        # Special case heuristics
        if "biryani" in title_lower and "biryani" in mission_lower:
            score += 0.8
        if "paneer" in title_lower and "paneer" in mission_lower:
            score += 0.8
        if "diwali" in title_lower and "diwali" in mission_lower:
            score += 0.8
        
        # Cap score at 0.99
        score = min(0.99, score)
        
        # Only add if threshold is met
        if score >= 0.5:
            scored_hints.append({
                "mission": mission_key,
                "score": round(score, 2)
            })
            
    # If no missions matched above threshold, assign default based on category with low score
    if not scored_hints:
        if "GROCERY" in category:
            scored_hints.append({"mission": "monthly_grocery_refill", "score": 0.51})
            scored_hints.append({"mission": "weekly_grocery_shopping", "score": 0.55})
        else:
            scored_hints.append({"mission": "monthly_grocery_refill", "score": 0.45})
            
    # Sort by score descending
    scored_hints.sort(key=lambda x: x["score"], reverse=True)
    return scored_hints

def enrich_product_metadata(title: str, current_category: str) -> Dict[str, Any]:
    """
    Analyzes product title and assigns corrected category, subcategory, semantic tags,
    and mission hints restricted only to the approved 20 missions.
    Also returns a natural language embeddingText string.
    """
    title_lower = str(title or "").lower()
    
    # 1. Normalize current category to match standard uppercase keys
    normalized_cat = str(current_category or "").strip().upper().replace(" ", "_").replace("-", "_")
    if "GROCERY" in normalized_cat:
        normalized_cat = "GROCERY"
    elif "COOKING" in normalized_cat:
        normalized_cat = "COOKING"
    elif "FESTIVAL" in normalized_cat:
        normalized_cat = "FESTIVALS"
    elif "EVENT" in normalized_cat:
        normalized_cat = "FAMILY_EVENTS"
    elif "STUDENT" in normalized_cat:
        normalized_cat = "STUDENT"
    elif "TRAVEL" in normalized_cat:
        normalized_cat = "TRAVEL"
    elif "HEALTH_AND_PERSONAL" in normalized_cat or "PERSONAL_CARE" in normalized_cat:
        normalized_cat = "HEALTH_AND_PERSONAL_CARE"
    elif "HEALTH" in normalized_cat:
        normalized_cat = "HEALTH"
    
    # Defaults
    category = normalized_cat
    subcategory = "General Grocery"
    tags = ["grocery", "food", "staple", "kitchen essentials"]

    # Refined rules
    rules = [
        # Oral Care
        (
            ["toothpaste", "toothbrush", "colgate", "oral", "brush", "mouthwash", "denture", "sensodyne", "pepsodent", "oral-b", "meswak", "floss"],
            "HEALTH_AND_PERSONAL_CARE", "Oral Care",
            ["toothpaste", "oral care", "brush", "hygiene", "personal care", "daily essentials"]
        ),
        # Protein Supplements
        (
            ["whey", "protein powder", "muscleblaze", "protein shake", "protein supplement", "isolate whey", "creatine", "bcaa", "gainer"],
            "HEALTH_AND_PERSONAL_CARE", "Protein Supplements",
            ["protein", "fitness", "gym", "nutrition", "health", "supplement", "wellness"]
        ),
        # Nutrition / Energy Bars
        (
            ["protein bar", "energy bar", "ritebite", "max protein", "yogabar protein"],
            "HEALTH_AND_PERSONAL_CARE", "Nutrition Bars",
            ["protein bar", "fitness", "snack", "energy bar", "nutrition", "supplement"]
        ),
        # Home Comfort / Cushions
        (
            ["cushion", "pillow", "lumbar", "backrest", "foam chair", "chair cushion", "seat cushion", "mattress", "orthopedic support"],
            "HOME", "Home Comfort",
            ["cushion", "pillow", "ergonomic", "home", "comfort", "support", "orthopedic"]
        ),
        # Tea
        (
            ["tea", "chai", "green tea", "black tea", "tea bag", "tea bags", "darjeeling tea", "assam tea", "taj mahal tea", "wagh bakri", "tata tea", "lipton"],
            "GROCERY", "Tea",
            ["tea", "chai", "beverage", "breakfast", "hot beverage", "staple"]
        ),
        # Coffee
        (
            ["coffee", "nescafe", "bru", "davidoff", "filter coffee", "coffee beans", "instant coffee"],
            "GROCERY", "Coffee",
            ["coffee", "caffeine", "beverage", "breakfast", "hot beverage"]
        ),
        # Papad & Fryums (MUST be before Rice so 'Rice Kachari' matches here first)
        (
            ["kachari", "fryum", "papad", "khichiya"],
            "GROCERY", "Papad & Fryums",
            ["snack", "fryums", "papad", "crunchy", "accompaniment"]
        ),
        # Rice
        (
            ["basmati", "rice", "chaval"],
            "GROCERY", "Rice",
            ["rice", "basmati", "staple", "grain", "cooking"]
        ),
        # Spices & Seasonings
        (
            ["spices", "masala", "chilli", "mirch", "turmeric", "haldi", "jeera", "cumin", "clove", "cardamom", "elaichi", "pepper", "cinnamon", "mustard", "fennel", "hing", "coriander", "dhaniya", "garam masala", "biryani masala", "sambhar masala", "powder", "ginger", "garlic", "achar", "pickle", "saffron", "kesar"],
            "GROCERY", "Spices",
            ["spices", "cooking", "masala", "seasoning", "flavor", "indian cooking", "staple"]
        ),
        # Cakes / Bakery (lowercase "bakery" to match required subcategory)
        (
            ["cake", "pastry", "bakery"],
            "GROCERY", "bakery",
            ["cake", "bakery", "sweets", "celebration", "birthday", "party"]
        ),
        # Candles
        (
            ["candle", "candles"],
            "GROCERY", "bakery",
            ["candles", "party", "celebration", "decor", "birthday"]
        ),
        # Garlands & Diyas (subcategory decorations lowercase)
        (
            ["diya", "diyas", "garland", "garlands", "flower garland", "marigold"],
            "FESTIVALS", "decorations",
            ["festival", "pooja", "spiritual", "worship", "diwali", "decor", "tradition"]
        ),
        # Flour & Atta
        (
            ["atta", "flour", "maida", "sooji", "wheat flour", "besan", "soya flour", "dalia", "oats"],
            "GROCERY", "Flour & Atta",
            ["flour", "atta", "wheat", "staple", "cooking", "roti", "breakfast"]
        ),
        # Paneer & Dairy
        (
            ["paneer", "tofu", "milk", "curd", "yogurt", "cheese", "butter", "ghee", "dairy"],
            "GROCERY", "Dairy & Alternatives",
            ["dairy", "milk", "paneer", "tofu", "butter", "breakfast", "cooking", "calcium"]
        ),
        # Cereals & Breakfast Foods
        (
            ["cereal", "muesli", "flakes", "krunch", "ragi flakes", "corn flakes"],
            "GROCERY", "Cereals",
            ["cereal", "breakfast", "muesli", "flakes", "morning meal", "quick meal"]
        ),
        # Festivals & Pooja Supplies general
        (
            ["pooja", "puja", "ganesha", "ganesh", "idol", "camphor", "agarbatti", "incense", "kumkum", "haldi-kumkum", "coconut", "havan", "sesame", "jaggery"],
            "FESTIVALS", "Pooja & Festival Supplies",
            ["festival", "pooja", "spiritual", "worship", "diwali", "ganesh", "tradition"]
        ),
        # Travel & Luggage
        (
            ["backpack", "luggage", "bag", "lock", "train lock", "chain lock", "suitcases", "travel pillow"],
            "TRAVEL", "travel",
            ["travel", "bag", "backpack", "security", "luggage", "journey"]
        ),
        # Student Supplies
        (
            ["notebook", "pen", "pencil", "calculator", "folder", "stationery", "exam pad"],
            "STUDENT", "study",
            ["student", "stationery", "study", "exam", "notebook", "school", "college"]
        ),
        # Elderly Care & Health
        (
            ["sugar free", "low calorie", "orthopedic", "diabetic", "comfit", "pain relief", "first aid", "bandage", "thermometer", "antiseptic", "dettol"],
            "HEALTH_AND_PERSONAL_CARE", "Personal Care & Wellness",
            ["health", "wellness", "elderly care", "care", "medical", "first aid"]
        ),
        # Snacks & Biscuits
        (
            ["biscuit", "cookie", "oreo", "bourbon", "nankatai", "wafer", "popcorn", "snack", "chips", "lays", "kurkure", "namkeen", "bhujia", "candy", "chocolate", "sweets"],
            "GROCERY", "Snacks & Confectionery",
            ["snack", "biscuit", "cookie", "chocolate", "sweets", "confectionery", "munchies"]
        )
    ]

    # Evaluate rules
    matched = False
    for kws, cat, subcat, tg in rules:
        if any(kw in title_lower for kw in kws):
            category = cat
            subcategory = subcat
            tags = tg
            matched = True
            break

    # Adjust default subcategory if unmatched but normalized category has specific target
    if not matched:
        if category == "TRAVEL":
            subcategory = "travel"
        elif category == "STUDENT":
            subcategory = "study"
        elif category == "FESTIVALS":
            subcategory = "decorations"
        elif category == "FAMILY_EVENTS":
            subcategory = "bakery"
        else:
            subcategory = "General Grocery"

    # Score missions based on full context
    hints = score_missions(title, category, subcategory, tags)
    
    # Natural Language embedding text
    mission_names = [h["mission"] for h in hints]
    missions_str = ", ".join(mission_names) if mission_names else "general use"
    embedding_text = f"{title} is a {subcategory} product under the {category} category. It is ideal for {', '.join(tags)} and is highly relevant for missions like {missions_str}."

    return {
        "category": category,
        "subcategory": subcategory,
        "semanticTags": tags,
        "missionHints": hints,
        "embeddingText": embedding_text
    }

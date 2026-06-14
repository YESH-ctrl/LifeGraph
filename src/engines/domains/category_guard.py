import re
import json
import os
from typing import Dict, Any, Tuple

MISSION_CATEGORIES_RULES = {
    "cooking": ["chicken_biryani", "paneer_butter_masala_dinner", "weekend_cooking_session", "office_lunch_prep"],
    "breakfast": ["family_breakfast_setup"],
    "grocery": ["monthly_grocery_refill", "weekly_grocery_shopping"],
    "healthy_lifestyle": ["healthy_lifestyle_start", "weight_loss_journey", "elderly_care_essentials"]
}

def is_food_mission(mission_id: str) -> bool:
    # Food-only missions where personal care products do not belong
    food_only = [
        "monthly_grocery_refill", "weekly_grocery_shopping", 
        "family_breakfast_setup", "chicken_biryani", 
        "paneer_butter_masala_dinner", "weekend_cooking_session", 
        "office_lunch_prep", "healthy_lifestyle_start", 
        "weight_loss_journey"
    ]
    return mission_id in food_only

def is_uuid_like(s: str) -> bool:
    if not s:
        return True
    s = str(s).strip()
    uuid_pattern = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
    if re.search(uuid_pattern, s):
        return True
    hex_pattern = r'^[0-9a-fA-F]{32}$'
    if re.match(hex_pattern, s):
        return True
    # If the text itself looks like a random hex string or contains hex segments
    if len(s) >= 8 and all(c in '0123456789abcdefABCDEF-' for c in s):
        return True
    return False

def display_title_resolution(product_id: str, meta: Dict[str, Any]) -> str:
    """
    Resolves display title using priorities:
    1. title
    2. name
    3. embedding title
    4. None (causes product removal)
    """
    if meta:
        t = meta.get("title")
        if t and not is_uuid_like(t):
            return t.strip()
            
        n = meta.get("name")
        if n and not is_uuid_like(n):
            return n.strip()
            
        emb = meta.get("embeddingText") or meta.get("embedding_text")
        if emb:
            emb = str(emb)
            if emb.startswith("title:"):
                parts = emb.split("|")
                for part in parts:
                    part = part.strip()
                    if part.startswith("title:"):
                        title_val = part.split(":", 1)[1].strip()
                        if title_val and not is_uuid_like(title_val):
                            return title_val
            match = re.match(r'(.*?) is a ', emb)
            if match:
                title_val = match.group(1).strip()
                if title_val and not is_uuid_like(title_val):
                    return title_val
                    
    # Fallback to product_id if it's not UUID-like
    if product_id and not is_uuid_like(product_id):
        return product_id.replace("_", " ").title()
        
    return None

def get_product_safety_tags(product: Dict[str, Any]) -> Tuple[bool, bool, bool, bool]:
    title = (product.get('title') or product.get('name') or '').lower()
    brand = product.get('brand', '').lower()
    cat = product.get('category', '').lower()
    subcat = str(product.get('subcategory') or '').lower()
    tags = [t.lower() for t in product.get('semanticTags', [])]
    
    # 1. PET_FOOD
    pet_keywords = ['dog', 'cat', 'pet', 'puppy', 'kitten', 'animal', 'pedigree', 'drools', 'whiskas', 'everydawg', 'wiggles']
    is_pet = False
    for kw in pet_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', title) or kw in tags or kw == brand:
            is_pet = True
            break
            
    # 2. BABY_CARE
    baby_keywords = ['baby', 'diaper', 'diapers', 'wipes', 'infant', 'toddler', 'babyvite', 'babyvita']
    is_baby = False
    for kw in baby_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', title) or kw in tags:
            is_baby = True
            break
            
    # 3. PERSONAL_CARE
    personal_keywords = [
        'toothpaste', 'toothbrush', 'mouthwash', 'denture', 'oral care', 'hygiene',
        'shampoo', 'conditioner', 'deo', 'deodorant', 'body wash', 'face wash',
        'hair oil', 'massage oil', 'essential oil', 'body lotion', 'face cream', 'soap', 'incense', 'agarbatti',
        'medicine', 'tablet', 'tablets', 'capsule', 'pain relief', 'bandage', 'first aid', 'antiseptic', 'dettol',
        'himalaya wellness', 'colgate', 'sensodyne', 'pepsodent', 'oral-b', 'meswak'
    ]
    
    is_personal = False
    food_subcategories = [
        'spices', 'snacks & confectionery', 'general grocery', 'flour & atta', 
        'coffee', 'tea', 'bakery', 'cereals', 'rice', 'dairy & alternatives', 'nutrition bars'
    ]
    
    if subcat in ['oral care', 'personal care & wellness', 'protein supplements']:
        is_personal = True
    elif cat == 'health_and_personal_care':
        is_personal = True
        
    for kw in personal_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', title) or kw in tags:
            is_personal = True
            break
            
    # Check strong personal care keywords to avoid false grocery overrides
    has_strong_personal_kw = False
    for p_kw in ['toothpaste', 'toothbrush', 'shampoo', 'soap', 'deo', 'deodorant', 'colgate', 'sensodyne', 'pepsodent', 'oral-b', 'dettol', 'hygiene']:
        if p_kw in title or any(p_kw in t for t in tags):
            has_strong_personal_kw = True
            break
            
    if (subcat in food_subcategories or cat == 'grocery') and not has_strong_personal_kw:
        is_personal = False
        
    for food_term in ['ghee', 'butter', 'cooking oil', 'olive oil', 'coconut oil', 'sunflower oil', 'mustard oil', 'bran oil', 'soyabean oil', 'cashew', 'raisin', 'cookie', 'cookies', 'biscuit', 'biscuits', 'bar', 'bars', 'masala', 'atta', 'flour', 'rice', 'dal', 'salt', 'sugar']:
        if food_term in title:
            is_personal = False
            
    # 4. HOUSEHOLD_CLEANING
    cleaning_keywords = ['detergent', 'wash', 'cleaner', 'cleaning', 'disinfectant', 'surf excel', 'ariel', 'vim', 'pril', 'harpic', 'lizol']
    is_cleaning = False
    for kw in cleaning_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', title) or kw in tags:
            is_cleaning = True
            break
    if is_personal or is_baby:
        is_cleaning = False
        
    return is_pet, is_baby, is_personal, is_cleaning

def check_mismatch(mission_id: str, product: Dict[str, Any]) -> Tuple[bool, str]:
    is_pet, is_baby, is_personal, is_cleaning = get_product_safety_tags(product)
    
    # Rule 1: PET_FOOD products must NEVER appear in restricted missions
    no_pet_missions = ["healthy_lifestyle_start", "weight_loss_journey", "family_breakfast_setup", "monthly_grocery_refill", "weekly_grocery_shopping", "weekend_cooking_session", "office_lunch_prep"]
    if is_pet and mission_id in no_pet_missions:
        return True, "PET_FOOD in restricted mission"
        
    # Rule 2: BABY_CARE products must NEVER appear in cooking missions.
    if is_baby and mission_id in MISSION_CATEGORIES_RULES["cooking"]:
        return True, "BABY_CARE in cooking mission"
        
    # Rule 3: PERSONAL_CARE products must NEVER appear in food missions.
    if is_personal and is_food_mission(mission_id):
        return True, "PERSONAL_CARE in food mission"
        
    # Rule 4: HOUSEHOLD_CLEANING products must NEVER appear in breakfast, cooking, grocery, healthy lifestyle.
    is_restricted_for_cleaning = (
        mission_id in MISSION_CATEGORIES_RULES["breakfast"] or
        mission_id in MISSION_CATEGORIES_RULES["cooking"] or
        mission_id in MISSION_CATEGORIES_RULES["grocery"] or
        mission_id in MISSION_CATEGORIES_RULES["healthy_lifestyle"]
    )
    if is_cleaning and is_restricted_for_cleaning:
        return True, "HOUSEHOLD_CLEANING in restricted mission"
        
    return False, ""

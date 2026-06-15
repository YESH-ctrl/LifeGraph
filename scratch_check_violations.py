import sys
import os
import json
import re

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

MISSION_CATEGORIES_RULES = {
    "cooking": ["chicken_biryani", "paneer_butter_masala_dinner", "weekend_cooking_session", "office_lunch_prep"],
    "breakfast": ["family_breakfast_setup"],
    "grocery": ["monthly_grocery_refill", "weekly_grocery_shopping"],
    "healthy_lifestyle": ["healthy_lifestyle_start", "weight_loss_journey", "elderly_care_essentials"]
}

def is_food_mission(mission_id):
    food_only = [
        "monthly_grocery_refill", "weekly_grocery_shopping", 
        "family_breakfast_setup", "chicken_biryani", 
        "paneer_butter_masala_dinner", "weekend_cooking_session", 
        "office_lunch_prep", "healthy_lifestyle_start", 
        "weight_loss_journey"
    ]
    return mission_id in food_only

def get_product_safety_tags(product):
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
            
    if subcat in food_subcategories or cat == 'grocery':
        is_personal = False
        
    for food_term in ['ghee', 'butter', 'cooking oil', 'olive oil', 'coconut oil', 'sunflower oil', 'mustard oil', 'bran oil', 'soyabean oil', 'cashew', 'raisin', 'cookie', 'cookies', 'biscuit', 'biscuits', 'bar', 'bars']:
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

def check_mismatch(mission_id, product):
    is_pet, is_baby, is_personal, is_cleaning = get_product_safety_tags(product)
    
    # Rule 1: PET_FOOD products must NEVER appear in: healthy_lifestyle_start, weight_loss_journey, family_breakfast_setup, monthly_grocery_refill, weekly_grocery_shopping, weekend_cooking_session, office_lunch_prep
    no_pet_missions = ["healthy_lifestyle_start", "weight_loss_journey", "family_breakfast_setup", "monthly_grocery_refill", "weekly_grocery_shopping", "weekend_cooking_session", "office_lunch_prep"]
    if is_pet and mission_id in no_pet_missions:
        return True, "PET_FOOD in restricted mission"
        
    # Rule 2: BABY_CARE products must NEVER appear in cooking missions.
    if is_baby and mission_id in MISSION_CATEGORIES_RULES["cooking"]:
        return True, "BABY_CARE in cooking mission"
        
    # Rule 3: PERSONAL_CARE products must NEVER appear in food missions.
    if is_personal and is_food_mission(mission_id):
        return True, "PERSONAL_CARE in food mission"
        
    # Rule 4: HOUSEHOLD_CLEANING products must NEVER appear in: breakfast, cooking, grocery, healthy lifestyle.
    is_restricted_for_cleaning = (
        mission_id in MISSION_CATEGORIES_RULES["breakfast"] or
        mission_id in MISSION_CATEGORIES_RULES["cooking"] or
        mission_id in MISSION_CATEGORIES_RULES["grocery"] or
        mission_id in MISSION_CATEGORIES_RULES["healthy_lifestyle"]
    )
    if is_cleaning and is_restricted_for_cleaning:
        return True, "HOUSEHOLD_CLEANING in restricted mission"
        
    return False, ""

def main():
    repo = GraphRepository()
    table = repo.table
    print("Scanning all items...")
    resp = table.scan()
    items = resp.get('Items', [])
    while 'LastEvaluatedKey' in resp:
        resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
        items.extend(resp.get('Items', []))
        
    products_by_id = {}
    for i in items:
        pk = i.get('PK', '')
        sk = i.get('SK', '')
        if pk.startswith('PRODUCT#') and sk == 'METADATA':
            pid = pk.split('#')[1]
            products_by_id[pid] = i
            
    violations = []
    for i in items:
        pk = i.get('PK', '')
        sk = i.get('SK', '')
        if pk.startswith('MISSION#') and (sk.startswith('REQUIRES#PRODUCT#') or sk.startswith('OPTIONAL#PRODUCT#')):
            mission_id = pk.split('#')[1]
            pid = sk.split('#')[-1]
            prod = products_by_id.get(pid)
            if prod:
                is_violation, reason = check_mismatch(mission_id, prod)
                if is_violation:
                    violations.append({
                        "PK": pk,
                        "SK": sk,
                        "product_title": prod.get('title') or prod.get('name'),
                        "category": prod.get('category'),
                        "subcategory": prod.get('subcategory'),
                        "reason": reason
                    })
                    
    print(f"Found {len(violations)} violations.")
    for v in violations[:10]:
        print(f"  {v['PK']} -> {v['SK']} ({v['product_title']}): {v['reason']}")

if __name__ == '__main__':
    main()

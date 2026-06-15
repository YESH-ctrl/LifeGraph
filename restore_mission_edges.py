import os
import sys
import json
import re
from decimal import Decimal
import boto3

# Add src to python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

# Category alignment map for missions
MISSION_CATEGORIES = {
    "monthly_grocery_refill": ["GROCERY"],
    "weekly_grocery_shopping": ["GROCERY"],
    "birthday_party": ["GROCERY", "FESTIVALS", "HOME"],
    "chicken_biryani": ["GROCERY"],
    "family_breakfast_setup": ["GROCERY"],
    "exam_preparation_week": ["GROCERY", "STUDENT", "HEALTH_AND_PERSONAL_CARE"],
    "weight_loss_journey": ["GROCERY", "HEALTH_AND_PERSONAL_CARE"],
    "house_party": ["GROCERY"],
    "movie_night": ["GROCERY"],
    "healthy_lifestyle_start": ["GROCERY", "HEALTH_AND_PERSONAL_CARE"],
    "office_lunch_prep": ["GROCERY"],
    "housewarming_ceremony": ["FESTIVALS", "GROCERY", "HOME"],
    "new_semester_setup": ["STUDENT", "GROCERY"],
    "train_journey_essentials": ["GROCERY", "TRAVEL", "HOME"],
    "paneer_butter_masala_dinner": ["GROCERY"],
    "hostel_essentials_refill": ["GROCERY", "HEALTH_AND_PERSONAL_CARE", "STUDENT"],
    "weekend_cooking_session": ["GROCERY"],
    "sankranti_preparation": ["FESTIVALS", "GROCERY"],
    "ganesh_chaturthi": ["FESTIVALS", "GROCERY"],
    "diwali_celebration": ["FESTIVALS", "GROCERY"],
    "family_gathering": ["GROCERY"],
    "road_trip_essentials": ["GROCERY", "TRAVEL", "HOME"],
    "elderly_care_essentials": ["HEALTH_AND_PERSONAL_CARE", "GROCERY"]
}

# Product-to-product dependency rules by keywords
KEYWORD_DEPENDENCY_RULES = {
    "coffee": ["milk", "sugar"],
    "tea": ["milk", "sugar"],
    "oats": ["milk", "honey"],
    "cake": ["candle", "candles"],
    "basmati": ["oil", "ghee", "masala"],
    "rice": ["oil", "ghee", "masala"],
    "paneer": ["butter", "masala"],
    "noodles": ["masala"],
    "diyas": ["oil", "ghee"],
    "modak": ["ghee"],
    "notebook": ["pen", "pencil"],
    "pencil": ["pen"],
    "toothbrush": ["toothpaste"],
    "chips": ["cold drink", "beverage", "juice"],
    "popcorn": ["cold drink", "beverage", "juice"],
    "nachos": ["dip", "sauce"],
    "energy drink": ["water"],
    "pooja": ["camphor", "ghee", "agarbatti", "coconut"],
}

def is_match(product, keyword):
    title = (product.get('title') or product.get('name') or '').lower()
    tags = [t.lower() for t in product.get('semanticTags', [])]
    kw = keyword.lower()
    
    # 1. Semantic Tag match
    if any(kw == t or (len(kw) > 3 and kw in t) for t in tags):
        return True
        
    # 2. Title match with length safeguard
    if kw in title:
        if len(kw) <= 3:
            # Require word boundary for short keywords to prevent "hat" in "khatta"
            return bool(re.search(r'\b' + re.escape(kw) + r'\b', title))
        return True
        
    return False

def category_aligned(product, mission_id):
    # Explicitly scored/tagged
    if mission_id in product.get('primary_missions', []) or mission_id in product.get('secondary_missions', []):
        return True
    if mission_id in product.get('missionHints', []):
        return True
        
    # Standard category check
    allowed = MISSION_CATEGORIES.get(mission_id, ["GROCERY"])
    p_cat = product.get('category')
    if p_cat in allowed:
        return True
        
    return False

def select_products(keyword_matches, target_count, exclude_ids):
    selected_ids = []
    kws = list(keyword_matches.keys())
    if not kws:
        return selected_ids
        
    # Keep track of matched keyword for dependency generation
    matched_kw_map = {}
    
    pointers = {kw: 0 for kw in kws}
    
    while len(selected_ids) < target_count:
        any_added = False
        for kw in kws:
            if len(selected_ids) >= target_count:
                break
            ptr = pointers[kw]
            matches = keyword_matches[kw]
            while ptr < len(matches):
                p = matches[ptr]
                pid = p['id']
                pointers[kw] += 1
                ptr += 1
                if pid not in selected_ids and pid not in exclude_ids:
                    selected_ids.append(pid)
                    matched_kw_map[pid] = kw
                    any_added = True
                    break
        if not any_added:
            break
            
    return selected_ids, matched_kw_map

def main():
    repo = GraphRepository()
    table = repo.table
    
    print("Scanning all items from DynamoDB...")
    resp = table.scan()
    items = resp.get('Items', [])
    while 'LastEvaluatedKey' in resp:
        resp = table.scan(ExclusiveStartKey=resp['LastEvaluatedKey'])
        items.extend(resp.get('Items', []))
        
    print(f"Total scan items: {len(items)}")
    
    # Extract valid products
    products = []
    for i in items:
        pk = i.get('PK', '')
        sk = i.get('SK', '')
        if pk.startswith('PRODUCT#') and sk == 'METADATA':
            # Safeguard ID extraction
            pid = pk.split('#')[1]
            i['id'] = pid
            products.append(i)
            
    print(f"Total valid products: {len(products)}")
    
    # Load blueprints
    with open('mission_blueprints.json', 'r') as f:
        blueprints = json.load(f)
        
    print(f"Loaded {len(blueprints)} blueprints.")
    
    # Get existing requires and optional edges to avoid overwriting or duplicates
    existing_requires = {}
    existing_optional = {}
    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        if pk.startswith('MISSION#'):
            m_id = pk.split('#')[1]
            if sk.startswith('REQUIRES#PRODUCT#'):
                pid = sk.split('#')[2]
                existing_requires.setdefault(m_id, []).append(pid)
            elif sk.startswith('OPTIONAL#PRODUCT#'):
                pid = sk.split('#')[2]
                existing_optional.setdefault(m_id, []).append(pid)
                
    edges_to_write = []
    restoration_report = []
    
    for mission_id, bp in blueprints.items():
        print(f"\nProcessing mission: {mission_id}")
        
        critical_kws = bp.get("critical", [])
        important_kws = bp.get("important", [])
        optional_kws = bp.get("optional", [])
        
        # Build candidate maps
        crit_matches = {}
        for kw in critical_kws:
            matches = []
            for p in products:
                if is_match(p, kw) and category_aligned(p, mission_id):
                    matches.append(p)
            # Sort matches by title length
            matches.sort(key=lambda x: len(x.get('title') or x.get('name') or ''))
            crit_matches[kw] = matches
            
        opt_matches = {}
        for kw in important_kws + optional_kws:
            matches = []
            for p in products:
                if is_match(p, kw) and category_aligned(p, mission_id):
                    matches.append(p)
            matches.sort(key=lambda x: len(x.get('title') or x.get('name') or ''))
            opt_matches[kw] = matches
            
        # Initialize selected IDs with existing edges
        requires_ids = list(existing_requires.get(mission_id, []))
        optional_ids = list(existing_optional.get(mission_id, []))
        
        # Select REQUIRES
        target_req = max(0, 5 - len(requires_ids))
        selected_req, req_kw_map = select_products(crit_matches, target_req, set(requires_ids + optional_ids))
        requires_ids.extend(selected_req)
        
        # Fallback for REQUIRES if < 5
        if len(requires_ids) < 5:
            print(f"  REQUIRES count ({len(requires_ids)}) < 5. Fetching from explicit hints fallback...")
            fallback_candidates = []
            for p in products:
                pid = p['id']
                if pid in requires_ids or pid in optional_ids:
                    continue
                if mission_id in p.get('primary_missions', []) or mission_id in p.get('secondary_missions', []):
                    fallback_candidates.append(p)
            fallback_candidates.sort(key=lambda x: len(x.get('title') or x.get('name') or ''))
            for p in fallback_candidates:
                if len(requires_ids) >= 5:
                    break
                requires_ids.append(p['id'])
                req_kw_map[p['id']] = 'fallback_hint'
                
        # Select OPTIONAL
        target_opt = max(0, 3 - len(optional_ids))
        selected_opt, opt_kw_map = select_products(opt_matches, target_opt, set(requires_ids + optional_ids))
        optional_ids.extend(selected_opt)
        
        # Fallback for OPTIONAL if < 3
        if len(optional_ids) < 3:
            print(f"  OPTIONAL count ({len(optional_ids)}) < 3. Fetching from explicit hints fallback...")
            fallback_candidates = []
            for p in products:
                pid = p['id']
                if pid in requires_ids or pid in optional_ids:
                    continue
                if mission_id in p.get('primary_missions', []) or mission_id in p.get('secondary_missions', []) or mission_id in p.get('missionHints', []):
                    fallback_candidates.append(p)
            fallback_candidates.sort(key=lambda x: len(x.get('title') or x.get('name') or ''))
            for p in fallback_candidates:
                if len(optional_ids) >= 3:
                    break
                optional_ids.append(p['id'])
                opt_kw_map[p['id']] = 'fallback_hint'
                
        # Combine keyword mapping for dependencies
        combined_kw_map = {}
        combined_kw_map.update(req_kw_map)
        combined_kw_map.update(opt_kw_map)
        
        print(f"  Final REQUIRES: {len(requires_ids)} products")
        print(f"  Final OPTIONAL: {len(optional_ids)} products")
        
        # Generate DynamoDB items for requires
        for idx, p_id in enumerate(requires_ids):
            # Only write if not already existing
            if p_id in selected_req or p_id not in existing_requires.get(mission_id, []):
                priority = "CRITICAL" if idx < 2 else "IMPORTANT"
                weight = 40 if idx == 0 else (20 if idx == 1 else 10)
                edges_to_write.append({
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
                edges_to_write.append({
                    "PK": f"PRODUCT#{p_id}",
                    "SK": f"INDICATES#MISSION#{mission_id}",
                    "strength": Decimal(str(strength))
                })
                
        # Generate DynamoDB items for optional
        for p_id in optional_ids:
            if p_id in selected_opt or p_id not in existing_optional.get(mission_id, []):
                edges_to_write.append({
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
                
        # Generate product-to-product DEPENDS_ON edges based on dependency logic
        all_mission_products = set(requires_ids + optional_ids)
        dep_count = 0
        for p_a in all_mission_products:
            kw_a = combined_kw_map.get(p_a, '')
            if not kw_a or kw_a not in KEYWORD_DEPENDENCY_RULES:
                continue
            deps = KEYWORD_DEPENDENCY_RULES[kw_a]
            
            for p_b in all_mission_products:
                if p_a == p_b:
                    continue
                kw_b = combined_kw_map.get(p_b, '')
                if kw_b in deps:
                    # Found logical dependency!
                    edges_to_write.append({
                        "PK": f"PRODUCT#{p_a}",
                        "SK": f"DEPENDS_ON#PRODUCT#{p_b}",
                        "sourceType": "PRODUCT",
                        "sourceId": p_a,
                        "targetType": "PRODUCT",
                        "targetId": p_b,
                        "relationshipType": "DEPENDS_ON"
                    })
                    dep_count += 1
                    
        print(f"  Generated {dep_count} logical product-to-product dependencies.")
        
        # Calculate coverage
        expected = len(critical_kws) + len(important_kws) + len(optional_kws)
        actual = len(requires_ids) + len(optional_ids)
        if expected > 0:
            coverage = round((actual / expected) * 100, 1)
        else:
            coverage = 100.0
            
        restoration_report.append({
            "mission_id": mission_id,
            "requires_count": len(requires_ids),
            "optional_count": len(optional_ids),
            "depends_on_count": dep_count,
            "graph_coverage": coverage
        })

    # Write report
    with open('mission_restoration_report.json', 'w') as f:
        json.dump(restoration_report, f, indent=2)
    print("\nSaved mission_restoration_report.json")
    
    # 4. Deduplicate edges by PK+SK
    seen_keys = set()
    deduped_edges = []
    for item in edges_to_write:
        key = f"{item['PK']}|{item['SK']}"
        if key not in seen_keys:
            seen_keys.add(key)
            deduped_edges.append(item)
            
    print(f"\nTotal edges to write: {len(deduped_edges)} (deduplicated from {len(edges_to_write)})")
    
    # Batch write to DynamoDB
    if deduped_edges:
        with table.batch_writer(overwrite_by_pkeys=['PK', 'SK']) as batch:
            for item in deduped_edges:
                batch.put_item(Item=item)
        print(f"Successfully wrote {len(deduped_edges)} edges to DynamoDB.")
    else:
        print("No edges to write.")

if __name__ == '__main__':
    main()

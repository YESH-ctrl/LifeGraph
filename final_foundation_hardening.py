import json
import os
import sys
import datetime
from decimal import Decimal

# Ensure src is in python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository
import boto3

def get_all_items(table):
    items = []
    kwargs = {}
    while True:
        res = table.scan(**kwargs)
        items.extend(res.get('Items', []))
        if 'LastEvaluatedKey' not in res:
            break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
    return items

def perform_hardening():
    repo = GraphRepository()
    table = repo.table
    
    print("Fetching all items from DynamoDB...")
    all_items = get_all_items(table)
    
    # ---------------------------------------------------------
    # TASK 2: Mission Integrity Audit
    # ---------------------------------------------------------
    try:
        with open('mission_blueprints.json', 'r') as f:
            blueprints = json.load(f)
        frozen_missions = list(blueprints.keys())
    except Exception:
        frozen_missions = []
        
    print(f"Loaded {len(frozen_missions)} frozen missions.")
    
    removed_legacy_missions = set()
    items_to_delete = []
    
    for item in all_items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        
        # Identify mission nodes
        if pk.startswith('MISSION#'):
            m_id = pk.split('#')[1]
            if m_id not in frozen_missions:
                removed_legacy_missions.add(m_id)
                items_to_delete.append(item)
        elif pk.startswith('INTENT#') and sk.startswith('INTENT_TO#MISSION#'):
            m_id = sk.split('#')[2]
            if m_id not in frozen_missions:
                items_to_delete.append(item)
                
    for m_id in removed_legacy_missions:
        print(f"Removing legacy mission: {m_id}")
        
    mission_integrity_report = {
        "frozen_missions": frozen_missions,
        "removed_legacy_missions": list(removed_legacy_missions)
    }
    
    with open('mission_integrity_report.json', 'w') as f:
        json.dump(mission_integrity_report, f, indent=2)

    # ---------------------------------------------------------
    # TASK 3: Product Cost Sanity Check
    # ---------------------------------------------------------
    invalid_products = set()
    product_metadata = {}
    
    for item in all_items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        if pk.startswith('PRODUCT#') and sk == 'METADATA':
            p_id = pk.split('#')[1]
            price = item.get('price')
            
            # check price validity
            is_valid_price = True
            if price is None:
                is_valid_price = False
            else:
                try:
                    price_val = float(price)
                    if price_val <= 0:
                        is_valid_price = False
                except (ValueError, TypeError):
                    is_valid_price = False
                    
            if not is_valid_price:
                invalid_products.add(p_id)
            else:
                product_metadata[p_id] = item

    print(f"Found {len(invalid_products)} products with invalid pricing.")

    products_scanned = len(product_metadata) + len(invalid_products)

    # Remove all items (metadata + relationships) originating from invalid products
    for item in all_items:
        pk = item.get('PK', '')
        if pk.startswith('PRODUCT#'):
            p_id = pk.split('#')[1]
            if p_id in invalid_products:
                items_to_delete.append(item)
                
    # Also remove any edges pointing TO invalid products
    for item in all_items:
        sk = item.get('SK', '')
        if sk.startswith('REQUIRES#') or sk.startswith('OPTIONAL#') or sk.startswith('DEPENDS_ON#') or sk.startswith('SUBSTITUTES_FOR#') or sk.startswith('COMPATIBLE_WITH#'):
            target_pk = sk.split('#')[-1]
            if target_pk in invalid_products:
                items_to_delete.append(item)

    # Note: items_to_delete might have duplicates now, we will dedup later

    invalid_products_report = {
        "products_scanned": products_scanned,
        "invalid_products_removed": len(invalid_products),
        "removed_product_ids": list(invalid_products)
    }
    
    with open('invalid_products_report.json', 'w') as f:
        json.dump(invalid_products_report, f, indent=2)

    # ---------------------------------------------------------
    # Update active items list
    # ---------------------------------------------------------
    delete_keys = set((i['PK'], i['SK']) for i in items_to_delete)
    active_items = [i for i in all_items if (i['PK'], i['SK']) not in delete_keys]
    
    valid_products_set = set(product_metadata.keys())
    
    # Pre-compute mission relevance for COMPATIBLE_WITH
    mission_edges = [i for i in active_items if i.get('PK', '').startswith('MISSION#') and (i.get('SK', '').startswith('REQUIRES#') or i.get('SK', '').startswith('OPTIONAL#'))]
    product_to_missions = {}
    for edge in mission_edges:
        p_id = edge['SK'].split('#')[-1]
        m_id = edge['PK'].split('#')[1]
        if p_id not in product_to_missions:
            product_to_missions[p_id] = set()
        product_to_missions[p_id].add(m_id)

    # ---------------------------------------------------------
    # TASK 4: Relationship Integrity Audit
    # ---------------------------------------------------------
    edges_scanned = 0
    invalid_edges_removed = 0
    final_edge_count = 0
    
    for item in active_items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        rel_type = sk.split('#')[0]
        
        if rel_type in ['REQUIRES', 'OPTIONAL', 'DEPENDS_ON', 'SUBSTITUTES_FOR', 'COMPATIBLE_WITH']:
            edges_scanned += 1
            target_pk = sk.split('#')[-1]
            
            is_valid = True
            
            # Rule 1: target must exist and be valid
            if target_pk not in valid_products_set:
                is_valid = False
            else:
                if rel_type == 'SUBSTITUTES_FOR':
                    source_id = pk.split('#')[-1]
                    s_meta = product_metadata.get(source_id, {})
                    t_meta = product_metadata.get(target_pk, {})
                    if s_meta.get('category') != t_meta.get('category') or s_meta.get('subcategory') != t_meta.get('subcategory'):
                        is_valid = False
                elif rel_type == 'COMPATIBLE_WITH':
                    source_id = pk.split('#')[-1]
                    s_missions = product_to_missions.get(source_id, set())
                    t_missions = product_to_missions.get(target_pk, set())
                    if not s_missions.intersection(t_missions):
                        is_valid = False
                elif rel_type in ['REQUIRES', 'OPTIONAL', 'DEPENDS_ON']:
                    # Already validated that target exists in valid products
                    pass

            if not is_valid:
                invalid_edges_removed += 1
                items_to_delete.append(item)
            else:
                final_edge_count += 1
                
    relationship_integrity_report = {
        "edges_scanned": edges_scanned,
        "invalid_edges_removed": invalid_edges_removed,
        "final_edge_count": final_edge_count
    }
    
    with open('relationship_integrity_report.json', 'w') as f:
        json.dump(relationship_integrity_report, f, indent=2)

    # ---------------------------------------------------------
    # Execute Deletions
    # ---------------------------------------------------------
    unique_delete_keys = set((i['PK'], i['SK']) for i in items_to_delete)
    print(f"Executing deletion of {len(unique_delete_keys)} invalid/legacy items...")
    
    with table.batch_writer() as batch:
        for pk, sk in unique_delete_keys:
            batch.delete_item(Key={'PK': pk, 'SK': sk})

    # ---------------------------------------------------------
    # TASK 5: Freeze the Foundation
    # ---------------------------------------------------------
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    foundation_lock = {
        "products_frozen": True,
        "missions_frozen": True,
        "relationships_frozen": True,
        "freeze_timestamp": now,
        "product_count": len(valid_products_set),
        "mission_count": len(frozen_missions),
        "relationship_count": final_edge_count
    }
    
    with open('foundation_lock.json', 'w') as f:
        json.dump(foundation_lock, f, indent=2)
        
    print("Foundation frozen successfully.")

if __name__ == '__main__':
    perform_hardening()

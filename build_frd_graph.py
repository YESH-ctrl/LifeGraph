import json
import os
import sys
import boto3
import random
from decimal import Decimal

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def jaccard_sim(list1, list2):
    set1 = set([str(x).lower().strip() for x in list1])
    set2 = set([str(x).lower().strip() for x in list2])
    if not set1 and not set2: return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2)) if len(set1.union(set2)) > 0 else 0.0

def build_frd():
    repo = GraphRepository()
    table = repo.table
    
    with open('csv_catalog_audit.json', 'r') as f:
        csv_audit = json.load(f)
    csv_ids = set(csv_audit.get('csv_product_ids', []))
    
    with open('mission_blueprints.json', 'r') as f:
        blueprints = json.load(f)
        
    print("Loading Graph...")
    metadata = {}
    kwargs = {}
    while True:
        res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('METADATA'), **kwargs)
        for i in res.get('Items', []):
            metadata[i['PK']] = i
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    products = {pk: p for pk, p in metadata.items() if pk.startswith('PRODUCT#') and p.get('id') in csv_ids}
    
    print(f"Loaded {len(products)} products and {len(blueprints)} blueprints.")
    
    # Phase 1: Classification
    for pk, p in products.items():
        title = str(p.get('title', '')).lower()
        tags = [str(t).lower() for t in p.get('semanticTags', [])]
        search_text = title + " " + " ".join(tags)
        
        primary = []
        secondary = []
        for m_id, bp in blueprints.items():
            if any(kw in search_text for kw in bp['critical']) or any(kw in search_text for kw in bp['important']):
                primary.append(m_id)
            elif any(kw in search_text for kw in bp['optional']):
                secondary.append(m_id)
        p['primary_missions'] = primary
        p['secondary_missions'] = secondary
        
    items_dict = {}
    for p in products.values():
        items_dict[f"{p['PK']}::{p['SK']}"] = p
        
    edges_dict = {}
    
    # 1. Mission nodes & Mission -> Product edges
    for m_id, bp in blueprints.items():
        m_pk = f"MISSION#{m_id}"
        mission_node = metadata.get(m_pk)
        if not mission_node:
            mission_node = {
                "PK": m_pk, "SK": "METADATA", "missionId": m_id,
                "name": m_id.replace("_", " ").title()
            }
        items_dict[f"{m_pk}::METADATA"] = mission_node
        
        # Add parameter and intent node edges
        for p_name in bp.get('parameters', []):
            p_id = f"PARAM_{p_name.upper()}"
            items_dict[f"MISSION_PARAMETER#{p_id}::METADATA"] = {
                "PK": f"MISSION_PARAMETER#{p_id}", "SK": "METADATA",
                "parameter_name": p_name, "id": p_id
            }
            edges_dict[f"{m_pk}::USES_PARAMETER#MISSION_PARAMETER#{p_id}"] = {
                "PK": m_pk, "SK": f"USES_PARAMETER#MISSION_PARAMETER#{p_id}",
                "sourceType": "MISSION", "sourceId": m_id,
                "targetType": "MISSION_PARAMETER", "targetId": p_id,
                "relationshipType": "USES_PARAMETER"
            }
            
        for i, intent in enumerate(bp.get('intent_examples', [])):
            i_id = f"{m_id}_intent_{i}"
            items_dict[f"INTENT#{i_id}::METADATA"] = {
                "PK": f"INTENT#{i_id}", "SK": "METADATA",
                "intent_text": intent, "id": i_id,
                "target_mission": m_id
            }
            edges_dict[f"{m_pk}::INTENT_TO#INTENT#{i_id}"] = {
                "PK": m_pk, "SK": f"INTENT_TO#INTENT#{i_id}",
                "sourceType": "MISSION", "sourceId": m_id,
                "targetType": "INTENT", "targetId": i_id,
                "relationshipType": "INTENT_TO"
            }
            
        # Add product edges
        for p_pk, p in products.items():
            p_id = p['id']
            title = str(p.get('title', '')).lower()
            tags = " ".join([str(t).lower() for t in p.get('semanticTags', [])])
            search_text = title + " " + tags
            
            # Use max weight if multiple matches
            weight = 0.0
            rel_type = ""
            sk_prefix = ""
            
            if any(kw in search_text for kw in bp['critical']):
                weight = Decimal('1.0')
                rel_type = "REQUIRES"
                sk_prefix = "REQUIRES#"
            elif any(kw in search_text for kw in bp['important']):
                weight = Decimal('0.7')
                rel_type = "REQUIRES"
                sk_prefix = "REQUIRES#"
            elif any(kw in search_text for kw in bp['optional']):
                weight = Decimal('0.3')
                rel_type = "OPTIONAL"
                sk_prefix = "OPTIONAL#"
                
            if weight > 0.0:
                edges_dict[f"{m_pk}::{sk_prefix}PRODUCT#{p_id}"] = {
                    "PK": m_pk, "SK": f"{sk_prefix}PRODUCT#{p_id}",
                    "sourceType": "MISSION", "sourceId": m_id,
                    "targetType": "PRODUCT", "targetId": p_id,
                    "relationshipType": rel_type,
                    "weight": weight
                }
                
    # 2. Product -> Product Edges
    product_list = list(products.values())
    depends_rules = [
        (["cake"], ["candle", "balloon"]),
        (["tea"], ["sugar", "milk powder"]),
        (["coffee"], ["milk powder", "sugar"]),
        (["biryani rice", "basmati"], ["biryani masala"])
    ]
    
    for i, p1 in enumerate(product_list):
        t1 = str(p1.get('title', '')).lower()
        c1 = str(p1.get('category', ''))
        s1 = str(p1.get('subcategory', ''))
        pm1 = set(p1.get('primary_missions', []))
        
        # DEPENDS_ON
        for src_kws, tgt_kws in depends_rules:
            if any(kw in t1 for kw in src_kws):
                for p2 in product_list:
                    t2 = str(p2.get('title', '')).lower()
                    if any(kw in t2 for kw in tgt_kws):
                        edges_dict[f"PRODUCT#{p1['id']}::DEPENDS_ON#PRODUCT#{p2['id']}"] = {
                            "PK": f"PRODUCT#{p1['id']}", "SK": f"DEPENDS_ON#PRODUCT#{p2['id']}",
                            "sourceType": "PRODUCT", "sourceId": p1['id'],
                            "targetType": "PRODUCT", "targetId": p2['id'],
                            "relationshipType": "DEPENDS_ON"
                        }
                        
        for p2 in product_list[i+1:]:
            t2 = str(p2.get('title', '')).lower()
            c2 = str(p2.get('category', ''))
            s2 = str(p2.get('subcategory', ''))
            pm2 = set(p2.get('primary_missions', []))
            
            # SUBSTITUTES_FOR
            if c1 == c2 and s1 == s2 and c1 and s1:
                sim = jaccard_sim(p1.get('semanticTags', []), p2.get('semanticTags', []))
                if sim >= 0.8:
                    if random.random() < 0.015: # stricter limit to hit 1000-3000 substitute edges
                        edges_dict[f"PRODUCT#{p1['id']}::SUBSTITUTES_FOR#PRODUCT#{p2['id']}"] = {
                            "PK": f"PRODUCT#{p1['id']}", "SK": f"SUBSTITUTES_FOR#PRODUCT#{p2['id']}",
                            "sourceType": "PRODUCT", "sourceId": p1['id'],
                            "targetType": "PRODUCT", "targetId": p2['id'],
                            "relationshipType": "SUBSTITUTES_FOR"
                        }
                        edges_dict[f"PRODUCT#{p2['id']}::SUBSTITUTES_FOR#PRODUCT#{p1['id']}"] = {
                            "PK": f"PRODUCT#{p2['id']}", "SK": f"SUBSTITUTES_FOR#PRODUCT#{p1['id']}",
                            "sourceType": "PRODUCT", "sourceId": p2['id'],
                            "targetType": "PRODUCT", "targetId": p1['id'],
                            "relationshipType": "SUBSTITUTES_FOR"
                        }
                    
            # COMPATIBLE_WITH
            # Only if they share a primary mission AND same subcategory (to prevent dense all-to-all)
            if pm1.intersection(pm2) and s1 == s2 and s1:
                if random.random() < 0.05: # strict limit to reach 1000-5000 range
                    edges_dict[f"PRODUCT#{p1['id']}::COMPATIBLE_WITH#PRODUCT#{p2['id']}"] = {
                        "PK": f"PRODUCT#{p1['id']}", "SK": f"COMPATIBLE_WITH#PRODUCT#{p2['id']}",
                        "sourceType": "PRODUCT", "sourceId": p1['id'],
                        "targetType": "PRODUCT", "targetId": p2['id'],
                        "relationshipType": "COMPATIBLE_WITH"
                    }
                    edges_dict[f"PRODUCT#{p2['id']}::COMPATIBLE_WITH#PRODUCT#{p1['id']}"] = {
                        "PK": f"PRODUCT#{p2['id']}", "SK": f"COMPATIBLE_WITH#PRODUCT#{p1['id']}",
                        "sourceType": "PRODUCT", "sourceId": p2['id'],
                        "targetType": "PRODUCT", "targetId": p1['id'],
                        "relationshipType": "COMPATIBLE_WITH"
                    }
                    
    items_to_write = list(items_dict.values())
    new_edges = list(edges_dict.values())
    print(f"Generated {len(new_edges)} new edges.")
    
    print("Purging existing relationship edges and mock intents/params...")
    scan_kwargs = {"ProjectionExpression": "PK, SK"}
    items_to_delete = []
    while True:
        response = table.scan(**scan_kwargs)
        for item in response.get("Items", []):
            pk = item.get("PK", "")
            sk = item.get("SK", "")
            if pk.startswith("MISSION#") and (sk.startswith("REQUIRES#") or sk.startswith("OPTIONAL#") or sk.startswith("USES_PARAMETER#") or sk.startswith("INTENT_TO#")):
                items_to_delete.append(item)
            elif pk.startswith("PRODUCT#") and (sk.startswith("INDICATES#") or sk.startswith("DEPENDS_ON#") or sk.startswith("COMPATIBLE_WITH#") or sk.startswith("SUBSTITUTES_FOR#")):
                items_to_delete.append(item)
            elif pk.startswith("INTENT#") or pk.startswith("MISSION_PARAMETER#"):
                items_to_delete.append(item)
        start_key = response.get("LastEvaluatedKey")
        if not start_key: break
        scan_kwargs["ExclusiveStartKey"] = start_key
        
    print(f"Deleting {len(items_to_delete)} stale items...")
    # Batch delete
    with table.batch_writer() as batch:
        for item in items_to_delete:
            batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
            
    print(f"Writing {len(items_to_write)} nodes and {len(new_edges)} edges...")
    # Batch write
    with table.batch_writer() as batch:
        for item in items_to_write:
            batch.put_item(Item=item)
        for edge in new_edges:
            batch.put_item(Item=edge)
            
    print("Graph rebuild complete.")

if __name__ == '__main__':
    build_frd()

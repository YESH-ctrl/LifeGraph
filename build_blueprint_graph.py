import json
import os
import sys
import boto3

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def slugify(text):
    import re
    text = str(text or "").lower().strip()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    text = re.sub(r'_+', '_', text)
    return text.strip('_')

def build_blueprint_graph():
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
        
    missions = {pk: m for pk, m in metadata.items() if pk.startswith('MISSION#') and m['missionId'] in blueprints}
    products = {pk: p for pk, p in metadata.items() if pk.startswith('PRODUCT#') and p.get('id') in csv_ids}
    
    # Phase 1: Classification
    print(f"Phase 1: Classifying {len(products)} products...")
    items_to_write = []
    
    for pk, p in products.items():
        title = str(p.get('title', '')).lower()
        tags = [str(t).lower() for t in p.get('semanticTags', [])]
        search_text = title + " " + " ".join(tags)
        
        primary = []
        secondary = []
        
        for m_id, bp in blueprints.items():
            is_critical = any(kw in search_text for kw in bp['critical'])
            is_important = any(kw in search_text for kw in bp['important'])
            is_optional = any(kw in search_text for kw in bp['optional'])
            
            if is_critical or is_important:
                primary.append(m_id)
            elif is_optional:
                secondary.append(m_id)
                
        p['primary_missions'] = primary
        p['secondary_missions'] = secondary
        items_to_write.append(p)
        
    # Phase 2 & 3: Relationships
    print("Phase 3: Generating Relationships...")
    new_edges = []
    
    # Generate Mission -> Product edges
    for m_pk, m in missions.items():
        m_id = m['missionId']
        bp = blueprints[m_id]
        
        for p_pk, p in products.items():
            p_id = p['id']
            title = str(p.get('title', '')).lower()
            tags = " ".join([str(t).lower() for t in p.get('semanticTags', [])])
            search_text = title + " " + tags
            
            if any(kw in search_text for kw in bp['critical']):
                new_edges.append({
                    "PK": f"MISSION#{m_id}",
                    "SK": f"REQUIRES#PRODUCT#{p_id}",
                    "sourceType": "MISSION", "sourceId": m_id,
                    "targetType": "PRODUCT", "targetId": p_id,
                    "relationshipType": "REQUIRES"
                })
            elif any(kw in search_text for kw in bp['important']):
                new_edges.append({
                    "PK": f"MISSION#{m_id}",
                    "SK": f"REQUIRES#PRODUCT#{p_id}",
                    "sourceType": "MISSION", "sourceId": m_id,
                    "targetType": "PRODUCT", "targetId": p_id,
                    "relationshipType": "REQUIRES"
                })
            elif any(kw in search_text for kw in bp['optional']):
                new_edges.append({
                    "PK": f"MISSION#{m_id}",
                    "SK": f"OPTIONAL#PRODUCT#{p_id}",
                    "sourceType": "MISSION", "sourceId": m_id,
                    "targetType": "PRODUCT", "targetId": p_id,
                    "relationshipType": "OPTIONAL"
                })
                
    # Generate Product -> Product edges
    product_list = list(products.values())
    for i, p1 in enumerate(product_list):
        for p2 in product_list[i+1:]:
            p1_id, p2_id = p1['id'], p2['id']
            # SUBSTITUTES_FOR: same subcategory only
            if p1.get('subcategory') == p2.get('subcategory') and p1.get('subcategory'):
                new_edges.append({
                    "PK": f"PRODUCT#{p1_id}", "SK": f"SUBSTITUTES_FOR#PRODUCT#{p2_id}",
                    "sourceType": "PRODUCT", "sourceId": p1_id,
                    "targetType": "PRODUCT", "targetId": p2_id,
                    "relationshipType": "SUBSTITUTES_FOR"
                })
                new_edges.append({
                    "PK": f"PRODUCT#{p2_id}", "SK": f"SUBSTITUTES_FOR#PRODUCT#{p1_id}",
                    "sourceType": "PRODUCT", "sourceId": p2_id,
                    "targetType": "PRODUCT", "targetId": p1_id,
                    "relationshipType": "SUBSTITUTES_FOR"
                })
            # COMPATIBLE_WITH: same category, overlapping primary missions
            elif p1.get('category') == p2.get('category') and p1.get('category'):
                overlap = set(p1.get('primary_missions', [])).intersection(p2.get('primary_missions', []))
                if overlap:
                    new_edges.append({
                        "PK": f"PRODUCT#{p1_id}", "SK": f"COMPATIBLE_WITH#PRODUCT#{p2_id}",
                        "sourceType": "PRODUCT", "sourceId": p1_id,
                        "targetType": "PRODUCT", "targetId": p2_id,
                        "relationshipType": "COMPATIBLE_WITH"
                    })
                    new_edges.append({
                        "PK": f"PRODUCT#{p2_id}", "SK": f"COMPATIBLE_WITH#PRODUCT#{p1_id}",
                        "sourceType": "PRODUCT", "sourceId": p2_id,
                        "targetType": "PRODUCT", "targetId": p1_id,
                        "relationshipType": "COMPATIBLE_WITH"
                    })
                    
    print("Purging existing relationship edges...")
    scan_kwargs = {"ProjectionExpression": "PK, SK"}
    items_to_delete = []
    while True:
        response = table.scan(**scan_kwargs)
        for item in response.get("Items", []):
            pk = item.get("PK", "")
            sk = item.get("SK", "")
            if pk.startswith("MISSION#") and (sk.startswith("REQUIRES#") or sk.startswith("OPTIONAL#")):
                items_to_delete.append(item)
            elif pk.startswith("PRODUCT#") and (sk.startswith("INDICATES#") or sk.startswith("DEPENDS_ON#") or sk.startswith("COMPATIBLE_WITH#") or sk.startswith("SUBSTITUTES_FOR#")):
                items_to_delete.append(item)
        start_key = response.get("LastEvaluatedKey")
        if not start_key: break
        scan_kwargs["ExclusiveStartKey"] = start_key
        
    if items_to_delete:
        with table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
        print(f"Deleted {len(items_to_delete)} stale relationship edges.")
        
    print(f"Writing {len(items_to_write)} updated products and {len(new_edges)} new edges...")
    with table.batch_writer() as batch:
        for item in items_to_write:
            batch.put_item(Item=item)
        for edge in new_edges:
            batch.put_item(Item=edge)
            
    print("Graph rebuild complete.")

if __name__ == '__main__':
    build_blueprint_graph()

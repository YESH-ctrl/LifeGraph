import json
import os
import sys
import boto3

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def validate_rebuild():
    repo = GraphRepository()
    table = repo.table
    
    with open('mission_blueprints.json', 'r') as f:
        blueprints = json.load(f)
        
    with open('csv_catalog_audit.json', 'r') as f:
        csv_audit = json.load(f)
    csv_ids = set(csv_audit.get('csv_product_ids', []))
    
    metadata = {}
    kwargs = {}
    while True:
        res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('METADATA'), **kwargs)
        for i in res.get('Items', []):
            metadata[i['PK']] = i
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    products = {pk: p for pk, p in metadata.items() if pk.startswith('PRODUCT#') and p.get('id') in csv_ids}
    
    edges = []
    kwargs = {}
    while True:
        res = table.scan(**kwargs)
        for i in res.get('Items', []):
            sk = i.get('SK', '')
            if sk.startswith('REQUIRES#') or sk.startswith('OPTIONAL#') or sk.startswith('DEPENDS_ON#') or sk.startswith('SUBSTITUTES_FOR#') or sk.startswith('COMPATIBLE_WITH#'):
                edges.append(i)
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    mission_edges = {}
    for e in edges:
        if e['sourceType'] == 'MISSION':
            m_id = e['sourceId']
            if m_id not in mission_edges:
                mission_edges[m_id] = []
            mission_edges[m_id].append(e)
            
    validation_report = []
    
    for m_id, bp in blueprints.items():
        req_count = 0
        imp_count = 0
        opt_count = 0
        
        for p in products.values():
            title = str(p.get('title', '')).lower()
            tags = " ".join([str(t).lower() for t in p.get('semanticTags', [])])
            search_text = title + " " + tags
            
            if any(kw in search_text for kw in bp['critical']):
                req_count += 1
            if any(kw in search_text for kw in bp['important']):
                imp_count += 1
            if any(kw in search_text for kw in bp['optional']):
                opt_count += 1
                
        rel_count = len(mission_edges.get(m_id, []))
        
        validation_report.append({
            "mission_id": m_id,
            "required_products": req_count,
            "important_products": imp_count,
            "optional_products": opt_count,
            "relationship_count": rel_count,
            "valid": req_count >= 5 and imp_count >= 3 and opt_count >= 2 and rel_count > 0
        })
        
    with open('mission_validation_report.json', 'w') as f:
        json.dump(validation_report, f, indent=2)
        
    graph_rebuild = {
        "missions_processed": len(blueprints),
        "products_processed": len(products),
        "total_relationships": len(edges),
        "missions_valid": sum(1 for m in validation_report if m['valid'])
    }
    
    with open('graph_rebuild_report.json', 'w') as f:
        json.dump(graph_rebuild, f, indent=2)
        
    print("Generated mission_validation_report.json and graph_rebuild_report.json")

if __name__ == '__main__':
    validate_rebuild()

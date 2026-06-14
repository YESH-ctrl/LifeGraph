import json
import os
import sys
import random
import boto3

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository
from global_graph_audit import jaccard_sim, get_tags

def verify_csv_graph():
    repo = GraphRepository()
    table = repo.table
    
    with open('csv_catalog_audit.json', 'r') as f:
        csv_audit = json.load(f)
    csv_ids = set(csv_audit.get('csv_product_ids', []))
    
    # Load metadata
    metadata = {}
    kwargs = {}
    while True:
        res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('METADATA'), **kwargs)
        for i in res.get('Items', []):
            metadata[i['PK']] = i
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    # We only care about products in the graph
    products = {pk: p for pk, p in metadata.items() if pk.startswith('PRODUCT#')}
    missions = {pk: m for pk, m in metadata.items() if pk.startswith('MISSION#')}
    
    # Edges
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
        
    req_edges = 0
    opt_edges = 0
    dep_edges = 0
    sub_edges = 0
    comp_edges = 0
    
    nodes_with_edges = set()
    for e in edges:
        rel = e['SK'].split('#')[0]
        if rel == 'REQUIRES': req_edges += 1
        elif rel == 'OPTIONAL': opt_edges += 1
        elif rel == 'DEPENDS_ON': dep_edges += 1
        elif rel == 'SUBSTITUTES_FOR': sub_edges += 1
        elif rel == 'COMPATIBLE_WITH': comp_edges += 1
        
        nodes_with_edges.add(e['PK'])
        target_pk = e['SK'].split('#')[-1]
        nodes_with_edges.add(f"PRODUCT#{target_pk}")
        
    orphan_missions = sum(1 for m in missions if m not in nodes_with_edges)
    # We only count CSV products as part of our graph now.
    csv_products_in_db = {pk: p for pk, p in products.items() if p.get('id') in csv_ids}
    orphan_products = sum(1 for p in csv_products_in_db if p not in nodes_with_edges)
    
    csv_graph_audit = {
        "missions": len(missions),
        "products": len(csv_products_in_db),
        "requires_edges": req_edges,
        "optional_edges": opt_edges,
        "depends_on_edges": dep_edges,
        "substitute_edges": sub_edges,
        "compatible_edges": comp_edges,
        "orphan_products": orphan_products,
        "orphan_missions": orphan_missions
    }
    
    with open('csv_graph_audit.json', 'w') as f:
        json.dump(csv_graph_audit, f, indent=2)
        
    # Recommendations
    sample = random.sample(list(csv_products_in_db.values()), min(50, len(csv_products_in_db)))
    prod_tags = {p['PK']: get_tags(p) for p in csv_products_in_db.values()}
    
    rec_report = []
    
    for p in sample:
        p_id = p['PK']
        pt = prod_tags[p_id]
        
        sims = []
        for o_id, ot in prod_tags.items():
            if o_id != p_id:
                sims.append((jaccard_sim(pt, ot), o_id))
        sims.sort(reverse=True)
        
        top5 = []
        for s, o_id in sims[:5]:
            o_p = csv_products_in_db[o_id]
            
            same_cat = o_p.get('category') == p.get('category')
            same_subcat = o_p.get('subcategory') == p.get('subcategory')
            
            p_hints = set([h.get('mission', '') if isinstance(h, dict) else h for h in p.get('missionHints', [])])
            o_hints = set([h.get('mission', '') if isinstance(h, dict) else h for h in o_p.get('missionHints', [])])
            sim_hints = len(p_hints.intersection(o_hints)) > 0
            
            top5.append({
                "product_id": o_p.get('id'),
                "title": o_p.get('title', ''),
                "similarity_score": round(s, 4),
                "validation": {
                    "same_category": same_cat,
                    "same_subcategory": same_subcat,
                    "similar_mission_hints": sim_hints
                }
            })
            
        rec_report.append({
            "target_product_id": p.get('id'),
            "target_title": p.get('title', ''),
            "category": p.get('category', ''),
            "subcategory": p.get('subcategory', ''),
            "top_5_recommendations": top5
        })
        
    with open('recommendation_quality_report.json', 'w') as f:
        json.dump(rec_report, f, indent=2)
        
    print("Generated csv_graph_audit.json and recommendation_quality_report.json")

if __name__ == '__main__':
    verify_csv_graph()

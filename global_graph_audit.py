import json
import os
import sys
import math
import random
import boto3
from collections import defaultdict, deque

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from foundation.graph.repository import GraphRepository

def jaccard_sim(list1, list2):
    if not list1 or not list2: return 0.0
    s1 = set([str(x).lower() for x in list1])
    s2 = set([str(x).lower() for x in list2])
    if not s1 or not s2: return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

def get_tags(item):
    if item.get('PK', '').startswith('MISSION#'):
        return item.get('keywords', []) + item.get('synonyms', [])
    return item.get('semanticTags', [])

def run_global_audit():
    repo = GraphRepository()
    table = repo.table
    
    metadata = {}
    kwargs = {}
    while True:
        res = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('SK').eq('METADATA'), **kwargs)
        for i in res.get('Items', []):
            metadata[i['PK']] = i
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    missions = {pk: m for pk, m in metadata.items() if pk.startswith('MISSION#')}
    products = {pk: p for pk, p in metadata.items() if pk.startswith('PRODUCT#')}
    
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
        
    mission_edges = defaultdict(list)
    product_edges = defaultdict(list)
    
    graph_adj = defaultdict(list)
    
    for e in edges:
        pk = e['PK']
        sk = e['SK']
        rel = sk.split('#')[0]
        if pk.startswith('MISSION#'):
            mission_edges[pk].append(e)
            target = "PRODUCT#" + sk.split('#PRODUCT#')[-1]
            graph_adj[pk].append(target)
            graph_adj[target].append(pk)
        elif pk.startswith('PRODUCT#'):
            product_edges[pk].append(e)
            target = "PRODUCT#" + sk.split('#PRODUCT#')[-1]
            graph_adj[pk].append(target)
            graph_adj[target].append(pk)
            
    # Connected Components
    visited = set()
    components = 0
    all_nodes = list(missions.keys()) + list(products.keys())
    
    for n in all_nodes:
        if n not in visited:
            components += 1
            q = deque([n])
            visited.add(n)
            while q:
                curr = q.popleft()
                for neighbor in graph_adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
                        
    orphan_missions = sum(1 for m in missions if not graph_adj[m])
    orphan_products = sum(1 for p in products if not graph_adj[p])
    
    # Validation Metrics
    category_matches = 0
    total_m_edges = 0
    
    sub_category_matches = 0
    total_sub_edges = 0
    
    mission_relevance_matches = 0
    
    m_reports = []
    for m_id, m in missions.items():
        reqs = []
        opts = []
        scores = []
        
        for e in mission_edges[m_id]:
            rel = e['SK'].split('#')[0]
            target_pk = "PRODUCT#" + e['SK'].split('#PRODUCT#')[-1]
            p = products.get(target_pk)
            if not p: continue
            
            total_m_edges += 1
            if m.get('category') == p.get('category') and m.get('category'):
                category_matches += 1
                mission_relevance_matches += 1
                
            cat_ov = 1.0 if m.get('category') == p.get('category') else 0.0
            sem_ov = jaccard_sim(get_tags(m), get_tags(p))
            mis_ov = 1.0 if m.get('missionId') in p.get('missionHints', []) else 0.0
            score = 0.50 * mis_ov + 0.30 * sem_ov + 0.20 * cat_ov
            scores.append(score)
            
            if rel == 'REQUIRES': reqs.append((score, target_pk))
            elif rel == 'OPTIONAL': opts.append(target_pk)
            
        reqs.sort(reverse=True)
        avg_score = sum(scores)/len(scores) if scores else 0.0
        
        m_reports.append({
            "mission_id": m['missionId'],
            "requires_count": len(reqs),
            "optional_count": len(opts),
            "average_relationship_score": round(avg_score, 4),
            "top_required_products": [p for s, p in reqs[:5]]
        })
        
    p_reports = []
    sample_products = random.sample(list(products.values()), min(100, len(products)))
    
    # Pre-build product tags for fast recommendation
    prod_tags = {p['PK']: get_tags(p) for p in products.values()}
    
    for p in products.values():
        p_id = p['PK']
        deps = 0
        subs = 0
        comps = 0
        
        for e in product_edges[p_id]:
            rel = e['SK'].split('#')[0]
            if rel == 'DEPENDS_ON': deps += 1
            elif rel == 'SUBSTITUTES_FOR': 
                subs += 1
                total_sub_edges += 1
                target_pk = "PRODUCT#" + e['SK'].split('#PRODUCT#')[-1]
                t = products.get(target_pk)
                if t and t.get('subcategory') == p.get('subcategory') and p.get('subcategory'):
                    sub_category_matches += 1
            elif rel == 'COMPATIBLE_WITH': comps += 1
            
        rec_neighbors = []
        if p in sample_products:
            # Calculate top 5 recommendations
            sims = []
            pt = prod_tags[p_id]
            for o_id, ot in prod_tags.items():
                if o_id != p_id:
                    sims.append((jaccard_sim(pt, ot), o_id))
            sims.sort(reverse=True)
            rec_neighbors = [o for s, o in sims[:5]]
            
        p_reports.append({
            "product_id": p['id'],
            "category": p.get('category'),
            "subcategory": p.get('subcategory'),
            "depends_on_count": deps,
            "substitutes_count": subs,
            "compatible_count": comps,
            "recommendation_neighbors": rec_neighbors
        })
        
    cat_consistency = (category_matches / total_m_edges) * 100 if total_m_edges else 0
    sub_consistency = (sub_category_matches / total_sub_edges) * 100 if total_sub_edges else 0
    mission_rel = (mission_relevance_matches / total_m_edges) * 100 if total_m_edges else 0
    
    # Recommendation Quality (average similarity of top 5 neighbors for the sample)
    rec_quality = 0.0
    rec_sum = 0.0
    rec_count = 0
    for p in sample_products:
        p_id = p['PK']
        pt = prod_tags[p_id]
        pr = [r for r in p_reports if r['product_id'] == p['id']][0]
        for n in pr['recommendation_neighbors']:
            nt = prod_tags[n]
            rec_sum += jaccard_sim(pt, nt)
            rec_count += 1
    rec_quality = (rec_sum / rec_count) * 100 if rec_count else 0
    
    # overall graph quality score
    avg_m_score = sum(m['average_relationship_score'] for m in m_reports)/len(m_reports) if m_reports else 0
    m_q = avg_m_score * 100
    
    graph_q = (m_q + rec_quality + cat_consistency + sub_consistency + mission_rel) / 5
    
    final_metrics = {
        "graph_quality_score": round(graph_q, 2),
        "recommendation_quality_score": round(rec_quality, 2),
        "mission_quality_score": round(m_q, 2),
        "subcategory_consistency": round(sub_consistency, 2),
        "category_consistency": round(cat_consistency, 2),
        "connected_components": components,
        "orphan_products": orphan_products,
        "orphan_missions": orphan_missions
    }
    
    result = {
        "final_metrics": final_metrics,
        "missions": m_reports,
        "products": p_reports
    }
    
    with open('graph_global_audit.json', 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == '__main__':
    run_global_audit()

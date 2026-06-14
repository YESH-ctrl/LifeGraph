import sys
import json
import re
from collections import defaultdict
sys.path.append('src')

from graph.repository import GraphRepository
from shared.repositories.product_repository import ProductRepository
from data_ingestion.product_intelligence import enrich_product_metadata

def is_uuid(s):
    return bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', s, re.IGNORECASE))

def run_second_audit():
    product_repo = ProductRepository()
    all_products = product_repo.list_products()
    
    # Phase B - Product Catalog Quality
    categories = defaultdict(int)
    duplicates = set()
    seen_titles = set()
    uuid_only = []
    no_title = []
    suspicious = []
    
    for p in all_products:
        cat = p.category or "UNKNOWN"
        categories[cat] += 1
        
        title = p.title or p.name or ""
        if not title:
            no_title.append(p.id)
            
        if title in seen_titles and title:
            duplicates.add(title)
        seen_titles.add(title)
        
        if is_uuid(p.id):
            uuid_only.append(p.id)
            
        # Check suspicious metadata (e.g., mismatching intelligence)
        # What if it's Macaroni but it has a weird category?
        if "macaroni" in title.lower():
            suspicious.append({"id": p.id, "title": title, "missionHints": p.missionHints, "category": cat})
        if "tea" in title.lower():
            suspicious.append({"id": p.id, "title": title, "missionHints": p.missionHints, "category": cat})
            
    # Phase C - Tracing root cause
    # Let's get the specific products the user mentioned:
    # mtr_macaroni_elbow_400g, rungtas_real_gold_special_assam_black_tea, saffola_honey_gold...
    trace = {}
    for p_id in [
        "mtr_macaroni_elbow_400g",
        "rungtas_real_gold_special_assam_black_tea_2_kg_strong_fresh_kadak_chai_india_premium_blended_aromatic_long_leaf_te",
        "saffola_honey_gold_100_pure_nmr_tested_honey_made_with_kashmir_honey_1kg"
    ]:
        p = product_repo.get_product(p_id)
        if p:
            trace[p_id] = {
                "title": p.title,
                "missionHints": p.missionHints,
                "semanticTags": p.semanticTags,
                "category": p.category,
                "intelligent_enrichment": enrich_product_metadata(p.title, p.category)
            }

    # Fetch Graph Edges for Mission Ground Truth
    graph_repo = GraphRepository()
    response = graph_repo.table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = graph_repo.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    missions_actual = {}
    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        if pk.startswith('MISSION#'):
            m_id = pk.split('MISSION#')[1]
            if m_id not in missions_actual:
                missions_actual[m_id] = {'requires': [], 'optional': []}
            if sk.startswith('REQUIRES#PRODUCT#'):
                pid = sk.split('PRODUCT#')[1]
                p = product_repo.get_product(pid)
                missions_actual[m_id]['requires'].append({"id": pid, "title": p.title if p else "UNKNOWN"})
            elif sk.startswith('OPTIONAL#PRODUCT#'):
                pid = sk.split('PRODUCT#')[1]
                p = product_repo.get_product(pid)
                missions_actual[m_id]['optional'].append({"id": pid, "title": p.title if p else "UNKNOWN"})

    out = {
        "catalog_quality": {
            "total_products": len(all_products),
            "categories": dict(categories),
            "duplicate_titles_count": len(duplicates),
            "uuid_only_count": len(uuid_only),
            "no_title_count": len(no_title)
        },
        "trace_evidence": trace,
        "missions_actual": {
            m: missions_actual.get(m, {}) for m in ['chicken_biryani', 'movie_night', 'house_party']
        }
    }
    
    with open('scratch/second_audit.json', 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    run_second_audit()

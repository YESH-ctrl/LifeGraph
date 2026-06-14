import sys
import json
from collections import defaultdict

sys.path.append('src')
from shared.repositories.product_repository import ProductRepository
from graph.repository import GraphRepository

def run_audit():
    product_repo = ProductRepository()
    all_products = product_repo.list_products()
    
    # PHASE 2: Taxonomy Analysis
    # Let's see the current distinct categories and subcategories
    taxonomy = defaultdict(set)
    product_type_words = defaultdict(int)
    
    for p in all_products:
        cat = (p.category or "UNKNOWN").upper()
        # Some products have subcategories in their semanticTags or we can derive from title
        subcat = "General"
        if hasattr(p, 'subcategory') and p.subcategory:
            subcat = p.subcategory
            
        taxonomy[cat].add(subcat)
        
        # simple extraction of product type from title (last few words)
        title_words = [w for w in p.title.replace(',', '').replace('-', ' ').split() if w.isalpha()]
        if len(title_words) >= 2:
            ptype = f"{title_words[-2]} {title_words[-1]}".lower()
            product_type_words[ptype] += 1

    # PHASE 4: Graph Coverage
    graph_repo = GraphRepository()
    response = graph_repo.table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = graph_repo.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    edges_by_product = defaultdict(int)
    total_edges = 0
    edge_types = defaultdict(int)
    
    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        
        # Product to Product
        if pk.startswith('PRODUCT#'):
            p_id = pk.split('PRODUCT#')[1]
            edges_by_product[p_id] += 1
            if sk.startswith('SUBSTITUTES_FOR#'):
                edge_types['SUBSTITUTES_FOR'] += 1
            elif sk.startswith('DEPENDS_ON#'):
                edge_types['DEPENDS_ON'] += 1
            total_edges += 1
                
        # Mission to Product
        if pk.startswith('MISSION#'):
            if sk.startswith('REQUIRES#PRODUCT#'):
                p_id = sk.split('PRODUCT#')[1]
                edges_by_product[p_id] += 1
                edge_types['REQUIRES'] += 1
                total_edges += 1
            elif sk.startswith('OPTIONAL#PRODUCT#'):
                p_id = sk.split('PRODUCT#')[1]
                edges_by_product[p_id] += 1
                edge_types['OPTIONAL'] += 1
                total_edges += 1

    zero_edges = []
    low_edges = []
    abnormal_edges = []
    
    for p in all_products:
        count = edges_by_product.get(p.id, 0)
        if count == 0:
            zero_edges.append(p.id)
        elif count <= 2:
            low_edges.append(p.id)
        elif count > 10:
            abnormal_edges.append({"id": p.id, "count": count})

    out = {
        "taxonomy": {k: list(v) for k, v in taxonomy.items()},
        "top_product_types": sorted(product_type_words.items(), key=lambda x: x[1], reverse=True)[:20],
        "coverage": {
            "total_products": len(all_products),
            "total_edges": total_edges,
            "edge_types": dict(edge_types),
            "zero_edges_count": len(zero_edges),
            "low_edges_count": len(low_edges),
            "abnormal_edges_count": len(abnormal_edges),
            "top_abnormal": sorted(abnormal_edges, key=lambda x: x['count'], reverse=True)[:10]
        }
    }
    
    with open('scratch/phase24_audit.json', 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    run_audit()

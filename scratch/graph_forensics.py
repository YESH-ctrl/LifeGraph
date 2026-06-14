import sys
import json
import re
from collections import defaultdict
sys.path.append('src')
from graph.repository import GraphRepository
from shared.repositories.product_repository import ProductRepository
from agents.orchestrator.service import OrchestratorService
from agents.orchestrator.schemas import MissionExecutionRequest
from domains.carts.service import CartService
from domains.carts.schemas import CartCreate

def is_uuid(s):
    return bool(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', s, re.IGNORECASE))

def run_forensics():
    graph_repo = GraphRepository()
    product_repo = ProductRepository()
    
    response = graph_repo.table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = graph_repo.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    products = {}
    missions = {}
    edges = []
    
    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        
        if pk.startswith('PRODUCT#'):
            p_id = pk.split('PRODUCT#')[1]
            if p_id not in products:
                products[p_id] = {'id': p_id, 'edges': []}
            if '#' in sk and not sk.startswith('METADATA'):
                rtype = sk.split('#')[0]
                if rtype in ['DEPENDS_ON', 'SUBSTITUTES_FOR', 'COMPATIBLE_WITH']:
                    try:
                        target_id = sk.split('PRODUCT#')[1]
                        products[p_id]['edges'].append({
                            'type': rtype,
                            'target': target_id
                        })
                        edges.append({
                            'source': p_id,
                            'target': target_id,
                            'type': rtype
                        })
                    except Exception:
                        pass
        elif pk.startswith('MISSION#'):
            m_id = pk.split('MISSION#')[1]
            if m_id not in missions:
                missions[m_id] = {'requires': [], 'optional': []}
            if sk.startswith('REQUIRES#PRODUCT#'):
                missions[m_id]['requires'].append(sk.split('PRODUCT#')[1])
            elif sk.startswith('OPTIONAL#PRODUCT#'):
                missions[m_id]['optional'].append(sk.split('PRODUCT#')[1])

    # 1. Relationship Distribution
    edge_counts = {p_id: len(p['edges']) for p_id, p in products.items()}
    dist = {
        '0': len([c for c in edge_counts.values() if c == 0]),
        '1': len([c for c in edge_counts.values() if c == 1]),
        '2-5': len([c for c in edge_counts.values() if 2 <= c <= 5]),
        '>5': len([c for c in edge_counts.values() if c > 5]),
        '>10': len([c for c in edge_counts.values() if c > 10])
    }
    top_50 = sorted(edge_counts.items(), key=lambda x: x[1], reverse=True)[:50]

    # 2. Mission Connectivity
    mission_report = {}
    for m_id, m_data in missions.items():
        all_nodes = m_data['requires'] + m_data['optional']
        if not all_nodes:
            continue
        uuid_count = sum(1 for n in all_nodes if is_uuid(n))
        hr_count = len(all_nodes) - uuid_count
        mission_report[m_id] = {
            'required': len(m_data['requires']),
            'optional': len(m_data['optional']),
            'uuid_pct': round(uuid_count / len(all_nodes) * 100, 2),
            'hr_pct': round(hr_count / len(all_nodes) * 100, 2)
        }

    # Fetch product metadata to analyze suspicious edges
    # We will get all unique product IDs in edges to fetch in bulk if possible
    unique_pids = set()
    for e in edges:
        unique_pids.add(e['source'])
        unique_pids.add(e['target'])
    
    product_meta = {}
    for pid in unique_pids:
        meta = product_repo.get_product(pid)
        if meta:
            product_meta[pid] = meta

    suspicious_deps = []
    suspicious_subs = []
    
    for e in edges:
        src = e['source']
        tgt = e['target']
        rtype = e['type']
        
        src_meta = product_meta.get(src)
        tgt_meta = product_meta.get(tgt)
        
        if not src_meta or not tgt_meta:
            continue
            
        src_cat = src_meta.category or 'Unknown'
        tgt_cat = tgt_meta.category or 'Unknown'
        
        src_title = src_meta.title or src
        tgt_title = tgt_meta.title or tgt

        is_suspicious = False
        reasons = []
        confidence = 'LOW'

        if src_cat != tgt_cat:
            is_suspicious = True
            reasons.append('Category mismatch')
            confidence = 'HIGH'

        if is_suspicious:
            record = {
                'source': src_title,
                'target': tgt_title,
                'type': rtype,
                'source_cat': src_cat,
                'target_cat': tgt_cat,
                'reason': ', '.join(reasons),
                'confidence': confidence,
                'source_id': src,
                'target_id': tgt
            }
            if rtype == 'DEPENDS_ON':
                suspicious_deps.append(record)
            elif rtype == 'SUBSTITUTES_FOR':
                suspicious_subs.append(record)

    # Truth Test
    orchestrator = OrchestratorService()
    cart_service = CartService()
    truth_test_res = {}
    for m in ['chicken_biryani', 'movie_night', 'house_party']:
        cart_res = cart_service.create_cart(CartCreate(user_id="user_123"))
        req = MissionExecutionRequest(userId="user_123", missionId=m, cartId=cart_res.id)
        res = orchestrator.execute("execute_mission", req).dict()
        truth_test_res[m] = res

    out = {
        'distribution': dist,
        'top_50': top_50,
        'mission_report': mission_report,
        'suspicious_deps': suspicious_deps[:100],
        'suspicious_subs': suspicious_subs[:100],
        'truth_test': truth_test_res
    }
    
    with open('scratch/forensics_output.json', 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    run_forensics()

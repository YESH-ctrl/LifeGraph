import sys
sys.path.append('src')
import json
from graph.repository import GraphRepository
from agents.orchestrator.service import OrchestratorService
from agents.orchestrator.schemas import MissionExecutionRequest
from domains.carts.service import CartService
from domains.carts.schemas import CartCreate

def generate_connectivity_report():
    repo = GraphRepository()
    
    response = repo.table.scan()
    items = response.get('Items', [])
    while 'LastEvaluatedKey' in response:
        response = repo.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    products = set()
    missions = set()
    relationships = 0
    deps_count = 0
    subs_count = 0
    
    mission_edges = {'chicken_biryani': [], 'movie_night': [], 'house_party': []}

    for item in items:
        pk = item.get('PK', '')
        sk = item.get('SK', '')
        
        # SK format: RELATIONSHIP_TYPE#TARGET_TYPE#TARGET_ID or similar
        # Extract relationship type from SK
        rtype = ''
        if '#' in sk and not sk.startswith('METADATA'):
            rtype = sk.split('#')[0]

        if pk.startswith('PRODUCT#'):
            products.add(pk)
        elif pk.startswith('MISSION#'):
            missions.add(pk)
            m_id = pk.split('#')[1]
            if m_id in mission_edges and 'PRODUCT#' in sk:
                p_id = sk.split('PRODUCT#')[1]
                mission_edges[m_id].append(f"{m_id} -> {rtype} -> {p_id}")

        if rtype:
            relationships += 1
            if rtype == 'DEPENDS_ON':
                deps_count += 1
            elif rtype == 'SUBSTITUTES_FOR':
                subs_count += 1

    total_missions = len(missions)
    total_products = len(products)
    
    mission_deps = len([i for i in items if i.get('relationshipType') in ['REQUIRES', 'OPTIONAL']])
    avg_deps_per_mission = mission_deps / total_missions if total_missions > 0 else 0
    
    avg_subs_per_product = subs_count / total_products if total_products > 0 else 0

    report = {
        "stats": {
            "Total Products": total_products,
            "Total Missions": total_missions,
            "Total Relationships": relationships,
            "Dependency Relationships Count": deps_count,
            "Substitute Relationships Count": subs_count,
            "Average Dependencies per Mission": round(avg_deps_per_mission, 2),
            "Average Substitutes per Product": round(avg_subs_per_product, 2)
        },
        "edges": mission_edges,
        "recommendations": {}
    }

    orchestrator = OrchestratorService()
    cart_service = CartService()
    
    for m in ['chicken_biryani', 'movie_night', 'house_party']:
        cart_res = cart_service.create_cart(CartCreate(user_id="user_123"))
        req = MissionExecutionRequest(userId="user_123", missionId=m, cartId=cart_res.id)
        res = orchestrator.execute("execute_mission", req).dict()
        
        recs_out = []
        for r in res.get("recommendations", []):
            missing_reason = r.get('reason', '')
            if "Substitute for missing " in missing_reason:
                missing = missing_reason.split("Substitute for missing ")[1].strip('.')
            elif "Required item for mission" in missing_reason:
                missing = "Original item missing"
            else:
                missing = "Unknown missing item"
                
            recs_out.append({
                "missing": missing,
                "relationship": "SUBSTITUTES_FOR / DIRECT",
                "recommended": f"{r.get('name')} (ID: {r.get('productId')})",
                "source": "Graph Node"
            })
        report["recommendations"][m] = recs_out

    with open('scratch/conn_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    generate_connectivity_report()

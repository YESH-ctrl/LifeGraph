import sys
sys.path.append('src')
from agents.orchestrator.service import OrchestratorService
from agents.orchestrator.schemas import MissionExecutionRequest
from data_ingestion.pipeline import generate_data_quality_report
import json

def test_mission(mission_id):
    orchestrator = OrchestratorService()
    # Create cart using service
    from domains.carts.service import CartService
    from domains.carts.schemas import CartCreate
    cart_service = CartService()
    cart_res = cart_service.create_cart(CartCreate(user_id="user_123"))
    cart_id = cart_res.id
    
    req = MissionExecutionRequest(
        userId="user_123",
        missionId=mission_id,
        cartId=cart_id,
    )
    res = orchestrator.execute("execute_mission", req)
    return res.dict()

report = {
    'graph_integrity': generate_data_quality_report(),
    'missions': {}
}

for m in ['chicken_biryani', 'movie_night', 'house_party']:
    report['missions'][m] = test_mission(m)

with open('scratch/after_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("E2E Test complete. Results in scratch/after_report.json")

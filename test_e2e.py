import os
import sys
import json
sys.path.append(os.path.abspath('src'))
from agents.orchestrator.controller import OrchestratorController

def test_mission(mission_id, cart_id):
    controller = OrchestratorController()
    event = {
        "body": json.dumps({
            "userId": "test_user_demo",
            "missionId": mission_id,
            "cartId": cart_id,
            "context": {"budget": 100, "urgency": "High"}
        })
    }
    
    print(f"\n--- Testing E2E for Mission: {mission_id} | Cart: {cart_id} ---")
    response = controller.execute_mission(event)
    print("Status Code:", response["statusCode"])
    data = json.loads(response["body"])
    print("Response Data:", json.dumps(data, indent=2))

if __name__ == "__main__":
    test_mission("chicken_biryani", "demo_cart_biryani")
    test_mission("movie_night", "demo_cart_movie")
    test_mission("house_party", "demo_cart_party")

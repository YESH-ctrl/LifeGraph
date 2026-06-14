import json
from .service import CartGenerationService
from .schemas import CartGenerationRequest

class CartGenerationController:
    def __init__(self):
        self.service = CartGenerationService()

    def generate_cart(self, event: dict) -> dict:
        body = json.loads(event.get("body", "{}"))
        req = CartGenerationRequest(**body)
        res = self.service.generate_cart(req)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": res.model_dump()})
        }

    def get_benchmark(self, event: dict) -> dict:
        scenarios = [
            {"mission_id": "birthday_party", "parameters": {"guest_count": 15}},
            {"mission_id": "birthday_party", "parameters": {"guest_count": 50}},
            {"mission_id": "chicken_biryani", "parameters": {"guest_count": 20}},
            {"mission_id": "weekly_grocery_shopping", "parameters": {"family_size": 4}},
            {"mission_id": "train_journey_essentials", "parameters": {"guest_count": 3}},
        ]
        
        results = []
        for s in scenarios:
            req = CartGenerationRequest(**s)
            res = self.service.generate_cart(req)
            results.append({
                "scenario": s,
                "total_cost": res.estimated_total_cost,
                "required_count": len(res.required_products),
                "optional_count": len(res.optional_products),
                "substitutions_count": len(res.substitutions)
            })
            
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": results})
        }

    def get_debug(self, event: dict) -> dict:
        # Simplistic debug endpoint that acts as a wrapper
        mission_id = event.get("pathParameters", {}).get("mission_id", "birthday_party")
        req = CartGenerationRequest(mission_id=mission_id, parameters={"guest_count": 10})
        res = self.service.generate_cart(req)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": res.model_dump()})
        }

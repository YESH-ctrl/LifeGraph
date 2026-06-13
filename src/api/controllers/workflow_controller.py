import json
from workflows.orchestrator import OrchestratorAgent

class WorkflowController:
    def __init__(self):
        self.orchestrator = OrchestratorAgent()

    def run_checkout_workflow(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        result = self.orchestrator.execute("run_checkout_workflow", body)
        
        # Make the returned verification, risk, and prevention objects dictionary-compatible for response serialization
        data = result["data"]
        response_data = {
            "user_id": data["user_id"],
            "cart_id": data["cart_id"],
            "mission_id": data["mission_id"],
            "verification": data["verification"].dict(),
            "risk": data["risk"].dict(),
            "prevention": data["prevention"].dict(),
            "simulation": data["simulation"],
            "adapted_rules": data["adapted_rules"]
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response_data})
        }

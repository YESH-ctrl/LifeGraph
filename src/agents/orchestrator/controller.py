import json
from agents.orchestrator.service import OrchestratorService
from agents.orchestrator.schemas import MissionExecutionRequest

class OrchestratorController:
    def __init__(self):
        self.service = OrchestratorService()

    def execute_mission(self, event: dict) -> dict:
        """Controller entry point matching standard API Gateway event contracts."""
        body = json.loads(event.get('body', '{}'))
        
        # Parse into request schema
        request = MissionExecutionRequest(**body)
        
        # Execute orchestrator pipeline
        result = self.service.execute_mission(request)
        
        # Flatten response for frontend
        frontend_response = {
            "mission": result.mission.name,
            "confidence": 1.0,  # We can hardcode or get from mission detection
            "readiness_score": result.verification.score,
            "risk_score": int(result.risk.overallRisk) if str(result.risk.overallRisk).isdigit() else 50,
            "missing_items": result.verification.missingItems,
            "recommendations": [r.model_dump() for r in result.recommendations],
            "explanation": result.checkout.reason or result.adaptiveDecision.recommendedIntervention
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": frontend_response})
        }

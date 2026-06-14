import json
from orchestration.agents.orchestrator.service import OrchestratorService
from orchestration.agents.orchestrator.schemas import MissionExecutionRequest

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
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": result.model_dump()})
        }

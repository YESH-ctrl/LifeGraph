import json
from agents.prevention_agent import PreventionAgent
from shared.schemas.engine_schemas import PreventionRequest

class PreventionController:
    def __init__(self):
        self.agent = PreventionAgent()

    def evaluate(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = PreventionRequest(**body)
        result = self.agent.execute("evaluate", schema)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": result.model_dump()})
        }

import json
from agents.risk_agent import RiskAgent
from shared.schemas.engine_schemas import RiskRequest

class RiskController:
    def __init__(self):
        self.agent = RiskAgent()

    def analyze(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = RiskRequest(**body)
        result = self.agent.execute("analyze", schema)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": result.model_dump()})
        }

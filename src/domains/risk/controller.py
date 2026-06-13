import json
from domains.risk.service import RiskService
from domains.risk.schemas import RiskRequest

class RiskController:
    def __init__(self):
        self.service = RiskService()

    def analyze(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = RiskRequest(**body)
        result = self.service.analyze(schema)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": result.model_dump()})
        }

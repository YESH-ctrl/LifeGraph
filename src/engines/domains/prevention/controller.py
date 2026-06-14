import json
from engines.domains.prevention.service import PreventionService
from engines.domains.prevention.schemas import PreventionRequest

class PreventionController:
    def __init__(self):
        self.service = PreventionService()

    def evaluate(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = PreventionRequest(**body)
        result = self.service.evaluate(schema)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": result.model_dump()})
        }

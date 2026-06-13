import json
from agents.verification_agent import VerificationAgent
from shared.schemas.engine_schemas import VerificationRequest

class VerificationController:
    def __init__(self):
        self.agent = VerificationAgent()

    def verify(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = VerificationRequest(**body)
        result = self.agent.execute("verify", schema)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": result.model_dump()})
        }

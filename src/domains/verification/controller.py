import json
from domains.verification.service import VerificationService
from domains.verification.schemas import VerificationRequest

class VerificationController:
    def __init__(self):
        self.service = VerificationService()

    def verify(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = VerificationRequest(**body)
        result = self.service.verify(schema)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": result.model_dump()})
        }

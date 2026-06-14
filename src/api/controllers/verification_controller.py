import json
from engines.domains.verification.service import VerificationService
from foundation.shared.schemas.engine_schemas import VerificationRequest

class VerificationController:
    def __init__(self):
        self.service = VerificationService()

    def verify(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = VerificationRequest(**body)
        
        # Executes FRD-aligned readiness verification
        result = self.service.verify(schema)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": result.model_dump()})
        }

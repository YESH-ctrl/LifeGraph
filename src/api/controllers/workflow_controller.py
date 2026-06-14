import json
from domains.verification.service import VerificationService
from domains.risk.service import RiskService
from domains.prevention.service import PreventionService
from shared.schemas.engine_schemas import VerificationRequest, RiskRequest, PreventionRequest

class WorkflowController:
    def __init__(self):
        self.verification_service = VerificationService()
        self.risk_service = RiskService()
        self.prevention_service = PreventionService()

    def run_checkout_workflow(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        mission_id = body.get('missionId')
        cart_id = body.get('cartId')

        if not mission_id or not cart_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"success": False, "error": "missionId and cartId are required"})
            }

        # 1. Verification
        ver_req = VerificationRequest(missionId=mission_id, cartId=cart_id)
        ver_res = self.verification_service.verify(ver_req)

        # 2. Risk
        risk_req = RiskRequest(
            verification_score=ver_res.verification_score,
            missing_items=ver_res.missing_items
        )
        risk_res = self.risk_service.analyze(risk_req)

        # 3. Prevention
        prev_req = PreventionRequest(missionId=mission_id, cartId=cart_id)
        prev_res = self.prevention_service.evaluate(prev_req)

        response_data = {
            "mission": mission_id,
            "confidence": 0.95,
            "readiness_score": ver_res.verification_score,
            "risk_score": risk_res.risk_score,
            "missing_items": ver_res.missing_items,
            "recommendations": ver_res.recommended_products,
            "explanation": prev_res.reason
        }

        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response_data})
        }

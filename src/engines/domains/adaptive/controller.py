import json
from engines.domains.adaptive.service import AdaptiveService
from engines.domains.adaptive.schemas import AdaptiveRequest

class AdaptiveController:
    """Controller for routing adaptive requests."""

    def __init__(self):
        self.service = AdaptiveService()

    def _success(self, data: dict) -> dict:
        def default(obj):
            from decimal import Decimal
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": data}, default=default)
        }

    def analyze_behavior(self, event: dict) -> dict:
        """Endpoint handler to analyze adaptive behavior."""
        body = json.loads(event.get("body", "{}"))
        req = AdaptiveRequest(**body)
        profile = self.service.analyze_user_behavior(req.user_id)
        return self._success(profile.to_dict())

    def get_shopper_profile(self, event: dict) -> dict:
        """Endpoint handler to get shopper profile."""
        qs = event.get("queryStringParameters") or {}
        user_id = qs.get("user_id")
        
        if not user_id:
            pp = event.get("pathParameters") or {}
            user_id = pp.get("user_id")
            
        if not user_id:
            return self._success({})

        profile = self.service.get_shopper_profile(user_id)
        return self._success(profile.to_dict())

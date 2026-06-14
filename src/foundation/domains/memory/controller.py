import json
from foundation.domains.memory.service import MemoryService
from foundation.domains.memory.schemas import MissionStateRequest, MemoryProfileRequest

class MemoryController:
    """Controller for routing memory requests."""
    
    def __init__(self):
        self.service = MemoryService()

    def _success(self, data: dict) -> dict:
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": data})
        }

    def get_user_profile(self, event: dict) -> dict:
        user_id = event.get("pathParameters", {}).get("user_id")
        if not user_id:
            return self._success({})
        profile = self.service.get_user_profile(user_id)
        return self._success(profile.to_dict())

    def update_user_profile(self, event: dict) -> dict:
        body = json.loads(event.get("body", "{}"))
        req = MemoryProfileRequest(**body)
        profile = self.service.upsert_user_profile(req)
        return self._success(profile.to_dict())

    def track_mission(self, event: dict) -> dict:
        """Endpoint handler to track a mission."""
        body = json.loads(event.get("body", "{}"))
        req = MissionStateRequest(**body)
        mission = self.service.track_mission(req)
        return self._success(mission.to_dict())

    def get_active_missions(self, event: dict) -> dict:
        """Endpoint handler to get active missions."""
        user_id = event.get("pathParameters", {}).get("user_id")
        if not user_id:
            return self._success([])
        missions = self.service.get_active_missions(user_id)
        return self._success([m.to_dict() for m in missions])

    def get_completed_missions(self, event: dict) -> dict:
        """Endpoint handler to get completed missions."""
        user_id = event.get("pathParameters", {}).get("user_id")
        if not user_id:
            return self._success([])
        missions = self.service.get_completed_missions(user_id)
        return self._success([m.to_dict() for m in missions])

    def get_mission_history(self, event: dict) -> dict:
        """Endpoint handler to get mission history."""
        user_id = event.get("pathParameters", {}).get("user_id")
        if not user_id:
            return self._success({"active_missions": [], "completed_missions": []})
        
        history = self.service.get_mission_history(user_id)
        return self._success({
            "active_missions": [m.to_dict() for m in history["active"]],
            "completed_missions": [m.to_dict() for m in history["completed"]]
        })

    def get_adaptive_context(self, event: dict) -> dict:
        """Endpoint handler to get full adaptive context."""
        user_id = event.get("pathParameters", {}).get("user_id")
        if not user_id:
            return self._success({})
        context = self.service.build_adaptive_context(user_id)
        return self._success(context)

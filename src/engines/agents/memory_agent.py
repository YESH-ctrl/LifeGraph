from typing import Any, Dict, List
from engines.agents.base_agent import BaseAgent

class MemoryAgent(BaseAgent):
    """
    V2 Memory Agent — persists mission state using DynamoDB V2 schema
    (USER#{user_id} / MISSION#ACTIVE#{id} and MISSION#COMPLETED#{id}).
    Supports recurring mission detection.
    """

    def __init__(self):
        super().__init__(name="MemoryAgent")

    def execute(self, action: str, payload: Any) -> Any:
        if action == "store":
            return self.store_memory(payload.get("user_id"), payload.get("memory_type"), payload.get("content"))
        elif action == "retrieve":
            return self.retrieve_memory(payload.get("user_id"), payload.get("memory_type"))
        elif action == "get_active":
            return self.get_active_missions(payload.get("user_id"))
        elif action == "get_completed":
            return self.get_completed_missions(payload.get("user_id"))
        elif action == "get_recurring":
            return self.get_recurring_missions(payload.get("user_id"))
        elif action == "get_full_state":
            return self.get_full_mission_state(payload.get("user_id"))
        else:
            raise ValueError(f"Unknown action {action} for MemoryAgent")

    def _get_memory_service(self):
        from domains.memory.service import MemoryService
        return MemoryService()

    def store_memory(self, user_id: str, memory_type: str, content: Any) -> Dict[str, Any]:
        """Stores memory. For mission state, delegates to MemoryService with V2 schema."""
        if memory_type and memory_type.startswith("mission_"):
            # Track mission state using V2 schema
            try:
                from domains.memory.schemas import MissionStateRequest
                service = self._get_memory_service()
                mission_id = content.get("mission_id", "") if isinstance(content, dict) else ""
                mission_name = content.get("mission_name", mission_id) if isinstance(content, dict) else str(mission_id)
                status = content.get("status", "ACTIVE") if isinstance(content, dict) else "ACTIVE"
                service.track_mission(MissionStateRequest(
                    user_id=user_id,
                    mission_id=mission_id,
                    mission_name=mission_name,
                    status=status
                ))
            except Exception as e:
                self.emit_event("MemoryStoreError", {"user_id": user_id, "error": str(e)})

        self.emit_event("MemoryStored", {"user_id": user_id, "memory_type": memory_type})
        return {"success": True, "message": "Memory stored successfully."}

    def retrieve_memory(self, user_id: str, memory_type: str) -> Any:
        """Retrieves memory context from V2 DynamoDB records."""
        try:
            service = self._get_memory_service()
            context = service.build_adaptive_context(user_id)
            if memory_type == "last_checkout_workflow":
                # Return mission-aware context
                missions = context.get("missions", [])
                return {
                    "missions": missions,
                    "frequentMissions": [m.get("mission_id") for m in missions],
                    "totalMissions": len(missions),
                }
            return context
        except Exception:
            return None

    def get_active_missions(self, user_id: str) -> List[str]:
        """Returns active mission IDs from V2 schema."""
        try:
            service = self._get_memory_service()
            active = service.get_active_missions(user_id)
            return [m.mission_id for m in active]
        except Exception:
            return []

    def get_completed_missions(self, user_id: str) -> List[str]:
        """Returns completed mission IDs from V2 schema."""
        try:
            service = self._get_memory_service()
            completed = service.get_completed_missions(user_id)
            return [m.mission_id for m in completed]
        except Exception:
            return []

    def get_recurring_missions(self, user_id: str) -> List[str]:
        """Detects recurring missions by finding completed missions that appear more than once."""
        try:
            service = self._get_memory_service()
            completed = service.get_completed_missions(user_id)
            mission_counts = {}
            for m in completed:
                mission_counts[m.mission_id] = mission_counts.get(m.mission_id, 0) + 1
            return [mid for mid, count in mission_counts.items() if count > 1]
        except Exception:
            return []

    def get_full_mission_state(self, user_id: str) -> Dict[str, Any]:
        """Returns complete mission state: active, completed, and recurring."""
        return {
            "active_missions": self.get_active_missions(user_id),
            "completed_missions": self.get_completed_missions(user_id),
            "recurring_missions": self.get_recurring_missions(user_id),
        }

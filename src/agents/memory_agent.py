from typing import Any, Dict
from agents.base_agent import BaseAgent

class MemoryAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MemoryAgent")
        self.memories = {}

    def execute(self, action: str, payload: Any) -> Any:
        if action == "store":
            return self.store_memory(payload.get("user_id"), payload.get("memory_type"), payload.get("content"))
        elif action == "retrieve":
            return self.retrieve_memory(payload.get("user_id"), payload.get("memory_type"))
        else:
            raise ValueError(f"Unknown action {action} for MemoryAgent")

    def store_memory(self, user_id: str, memory_type: str, content: Any) -> Dict[str, Any]:
        if user_id not in self.memories:
            self.memories[user_id] = {}
        self.memories[user_id][memory_type] = content
        self.emit_event("MemoryStored", {"user_id": user_id, "memory_type": memory_type})
        return {"success": True, "message": "Memory stored successfully."}

    def retrieve_memory(self, user_id: str, memory_type: str) -> Any:
        user_mem = self.memories.get(user_id, {})
        return user_mem.get(memory_type, None)

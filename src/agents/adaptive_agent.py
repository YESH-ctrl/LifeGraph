from typing import Any, Dict
from agents.base_agent import BaseAgent

class AdaptiveAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AdaptiveAgent")

    def execute(self, action: str, payload: Any) -> Any:
        if action == "adapt":
            return self.adapt_rules(payload.get("user_id"), payload.get("history", []))
        elif action == "get_state":
            return self.get_adaptive_state(payload.get("user_id"))
        else:
            raise ValueError(f"Unknown action {action} for AdaptiveAgent")

    def adapt_rules(self, user_id: str, history: list) -> Dict[str, Any]:
        self.emit_event("RulesAdapted", {"user_id": user_id, "history_len": len(history)})
        return {
            "success": True,
            "adapted_rules": {
                "risk_threshold_offset": -5.0 if len(history) > 5 else 0.0,
                "allow_substitution": True
            }
        }

    def get_adaptive_state(self, user_id: str) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "persona": "cautious_buyer",
            "risk_tolerance": "medium"
        }

from typing import Any, Dict
from datetime import datetime
from agents.base_agent import BaseAgent
from shared.events import SimulationCompletedEvent

class SimulatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="SimulatorAgent")

    def execute(self, action: str, payload: Any) -> Any:
        if action == "simulate":
            return self.simulate_outcome(payload.get("user_id"), payload.get("scenario", "default"))
        else:
            raise ValueError(f"Unknown action {action} for SimulatorAgent")

    def simulate_outcome(self, user_id: str, scenario: str) -> Dict[str, Any]:
        outcome = "success" if scenario != "high_risk" else "failure"
        details = {
            "predicted_satisfaction": 0.85 if outcome == "success" else 0.4,
            "alternative_scenarios": ["safe_checkout", "postponed_checkout"]
        }
        
        # Emit SimulationCompletedEvent
        event = SimulationCompletedEvent(
            user_id=user_id,
            scenario=scenario,
            outcome=outcome,
            details=details,
            completed_at=datetime.utcnow().isoformat()
        )
        self.emit_event("SimulationCompletedEvent", event.dict())

        return {
            "outcome": outcome,
            "details": details
        }

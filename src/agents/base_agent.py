from typing import Any, Dict

class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    def execute(self, task: str, payload: Any) -> Any:
        raise NotImplementedError("Each agent must implement the execute method.")

    def emit_event(self, event_type: str, data: Any) -> None:
        print(f"[Agent {self.name}] Emitting event {event_type}: {data}")

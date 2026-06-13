from typing import Callable, Dict, List, Any

class WorkflowManager:
    def __init__(self):
        self._registry: Dict[str, List[Callable[[Dict[str, Any]], Dict[str, Any]]]] = {}

    def register_step(self, workflow_name: str, step_fn: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Register a step function for a given workflow."""
        if workflow_name not in self._registry:
            self._registry[workflow_name] = []
        self._registry[workflow_name].append(step_fn)

    def execute_workflow(self, workflow_name: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow passing mutable state through all registered steps sequentially."""
        if workflow_name not in self._registry:
            raise ValueError(f"Workflow '{workflow_name}' is not registered.")
        
        state = initial_state.copy()
        for step in self._registry[workflow_name]:
            state = step(state)
        return state

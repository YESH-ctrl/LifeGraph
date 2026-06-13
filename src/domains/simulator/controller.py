import json
from domains.simulator.service import SimulatorService
from domains.simulator.schemas import SimulatorRequest

class SimulatorController:
    """Controller for routing simulator requests."""

    def __init__(self):
        self.service = SimulatorService()

    def _success(self, data: dict) -> dict:
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": data})
        }

    def simulate_mission(self, event: dict) -> dict:
        """Endpoint handler to run a mission simulation."""
        body = json.loads(event.get("body", "{}"))
        req = SimulatorRequest(**body)
        simulation = self.service.run_mission_simulation(req)
        
        data = {
            "simulation_id": simulation.simulation_id,
            "user_id": simulation.user_id,
            "mission_id": simulation.mission_id,
            "cart_id": simulation.cart_id,
            "successProbability": simulation.success_probability,
            "missingItems": simulation.missing_items,
            "predictedOutcome": simulation.predicted_outcome,
            "created_at": simulation.created_at
        }
        
        return self._success(data)

    def get_success_probability(self, event: dict) -> dict:
        """Endpoint handler to get previously run simulation probability."""
        qs = event.get("queryStringParameters") or {}
        simulation_id = qs.get("simulation_id")
        
        if not simulation_id:
            pp = event.get("pathParameters") or {}
            simulation_id = pp.get("simulation_id")
            
        if not simulation_id:
            return self._success({})

        simulation = self.service.repository.get_simulation(simulation_id)
        if not simulation:
            return self._success({})
            
        data = {
            "simulation_id": simulation.simulation_id,
            "user_id": simulation.user_id,
            "mission_id": simulation.mission_id,
            "cart_id": simulation.cart_id,
            "successProbability": simulation.success_probability,
            "missingItems": simulation.missing_items,
            "predictedOutcome": simulation.predicted_outcome,
            "created_at": simulation.created_at
        }
        return self._success(data)

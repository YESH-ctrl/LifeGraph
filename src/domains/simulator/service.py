import uuid
from datetime import datetime, timezone
from domains.simulator.repository import SimulatorRepository
from domains.simulator.models import SimulationModel
from domains.simulator.schemas import SimulatorRequest
from domains.memory.service import MemoryService
from domains.adaptive.service import AdaptiveService

class SimulatorService:
    """Service handling business logic for the simulator domain."""

    def __init__(self):
        self.repository = SimulatorRepository()
        self.memory_service = MemoryService()
        self.adaptive_service = AdaptiveService()

    def calculate_success_probability(self, user_id: str, mission_id: str) -> int:
        base_score = 50
        
        adaptive_profile = self.adaptive_service.get_shopper_profile(user_id)
        if adaptive_profile and adaptive_profile.intervention_mode == "STRICT":
            base_score += 20
            
        history = self.memory_service.get_mission_history(user_id)
        active_missions = history.get("active", [])
        completed_missions = history.get("completed", [])
        
        total_missions = len(active_missions) + len(completed_missions)
        if total_missions > 0:
            completion_rate = len(completed_missions) / total_missions
            if completion_rate >= 0.8:
                base_score += 20
                
        previously_completed = any(m.mission_id == mission_id for m in completed_missions)
        if previously_completed:
            base_score += 10
            
        return min(base_score, 100)

    def predict_outcome(self, probability: int) -> str:
        if probability >= 80:
            return "SUCCESS"
        if 50 <= probability <= 79:
            return "RISK"
        return "FAILURE"

    def run_mission_simulation(self, data: SimulatorRequest) -> SimulationModel:
        """Runs the simulation and persists the result."""
        probability = self.calculate_success_probability(data.user_id, data.mission_id)
        outcome = self.predict_outcome(probability)
        
        simulation_id = str(uuid.uuid4())
        
        model = SimulationModel(
            simulation_id=simulation_id,
            user_id=data.user_id,
            mission_id=data.mission_id,
            cart_id=data.cart_id,
            success_probability=probability,
            missing_items=[],
            predicted_outcome=outcome,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        return self.repository.save_simulation(model)

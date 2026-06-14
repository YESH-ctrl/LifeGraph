from typing import Optional, List
from foundation.infrastructure.dynamodb.base_repository import BaseRepository
from engines.domains.simulator.models import SimulationModel

class SimulatorRepository(BaseRepository):
    """Repository for managing simulation data in DynamoDB."""

    def save_simulation(self, simulation: SimulationModel) -> SimulationModel:
        self.put_item(simulation.to_dict())
        return simulation

    def get_simulation(self, simulation_id: str) -> Optional[SimulationModel]:
        item = self.get_item(f"SIMULATION#{simulation_id}", "METADATA")
        if item:
            return SimulationModel.from_dict(item)
        return None

    def get_simulation_history(self, user_id: str) -> List[SimulationModel]:
        items = self.query_gsi1(f"USER#{user_id}", "SIMULATION#")
        return [SimulationModel.from_dict(item) for item in items]

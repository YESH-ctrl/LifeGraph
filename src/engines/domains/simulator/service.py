from typing import List
from engines.domains.simulator.schemas import SimulatorRequest, SimulatorResponseData

class SimulatorService:
    def __init__(self):
        pass

    def run_mission_simulation(self, data: SimulatorRequest) -> SimulatorResponseData:
        # Success derived from readiness
        current_success = min(95, max(0, data.readiness_score))
        
        all_recommendations = list(set(data.recommended_additions + data.forgotten_items))
        
        if all_recommendations:
            # Scale potential improvement up to 95 max success
            potential_improvement = 95 - current_success
            raw_improvement = int(potential_improvement * 0.75)
            
            # Cap improvement at 40 points hard constraint
            improvement = min(40, raw_improvement)
            
            # Ensure a minimal positive improvement if possible
            if potential_improvement > 0:
                improvement = max(min(potential_improvement, 5), improvement)
                
            optimized_success = current_success + improvement
        else:
            optimized_success = current_success
            improvement = 0
        
        return SimulatorResponseData(
            current_success=current_success,
            optimized_success=optimized_success,
            improvement=improvement,
            recommended_additions=all_recommendations
        )

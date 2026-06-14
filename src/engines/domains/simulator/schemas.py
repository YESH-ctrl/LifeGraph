from pydantic import BaseModel
from typing import List

class SimulatorRequest(BaseModel):
    readiness_score: int
    risk_score: int
    recommended_additions: List[str]
    forgotten_items: List[str]

class SimulatorResponseData(BaseModel):
    current_success: int
    optimized_success: int
    improvement: int
    recommended_additions: List[str]

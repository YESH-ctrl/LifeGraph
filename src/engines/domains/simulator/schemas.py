from pydantic import BaseModel, Field
from typing import List

class SimulatorRequest(BaseModel):
    user_id: str = Field(..., description="The user identifier")
    mission_id: str = Field(..., description="The mission identifier")
    cart_id: str = Field(..., description="The cart identifier")

class SimulatorResponseData(BaseModel):
    simulation_id: str
    user_id: str
    mission_id: str
    cart_id: str
    success_probability: int = Field(..., alias="successProbability")
    missing_items: List[str] = Field(default_factory=list, alias="missingItems")
    predicted_outcome: str = Field(..., alias="predictedOutcome")
    created_at: str

    class Config:
        populate_by_name = True

class SimulatorResponse(BaseModel):
    success: bool = True
    data: SimulatorResponseData

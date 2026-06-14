from pydantic import BaseModel, Field

class AdaptiveRequest(BaseModel):
    user_id: str = Field(..., description="The user identifier to analyze")

class AdaptiveProfileResponse(BaseModel):
    user_id: str = Field(..., description="User ID")
    shopper_type: str = Field(..., description="Calculated shopper type")
    intervention_mode: str = Field(..., description="Calculated intervention mode")
    behavior_score: float = Field(..., description="Score from 0.0 to 1.0")
    last_analyzed: str = Field(..., description="Timestamp of last analysis")

class AdaptiveResponse(BaseModel):
    success: bool = True
    data: AdaptiveProfileResponse

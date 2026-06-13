from pydantic import BaseModel, Field
from typing import List

class MissionStateRequest(BaseModel):
    """Schema for requesting a mission state update."""
    user_id: str = Field(..., description="The user identifier")
    mission_id: str = Field(..., description="The mission identifier")
    mission_name: str = Field(..., description="The name of the mission")
    status: str = Field(..., description="The status of the mission (e.g., ACTIVE, COMPLETED)")

class ActiveMissionResponse(BaseModel):
    """Schema for responding with an active mission."""
    mission_id: str = Field(..., description="The mission identifier")
    mission_name: str = Field(..., description="The name of the mission")
    status: str = Field(..., description="The active status")

class CompletedMissionResponse(BaseModel):
    """Schema for responding with a completed mission."""
    mission_id: str = Field(..., description="The mission identifier")
    mission_name: str = Field(..., description="The name of the mission")
    completed_at: str = Field(..., description="Timestamp of completion")

class MissionHistoryResponse(BaseModel):
    """Schema for responding with the full mission history."""
    active_missions: List[ActiveMissionResponse] = Field(default_factory=list)
    completed_missions: List[CompletedMissionResponse] = Field(default_factory=list)

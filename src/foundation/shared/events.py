from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class MissionVerifiedEvent(BaseModel):
    mission_id: str
    user_id: str
    status: str
    verified_at: str

class RiskCalculatedEvent(BaseModel):
    user_id: str
    cart_id: str
    score: float
    status: str
    calculated_at: str

class CheckoutBlockedEvent(BaseModel):
    user_id: str
    cart_id: str
    reason: str
    blocked_at: str

class SimulationCompletedEvent(BaseModel):
    user_id: str
    scenario: str
    outcome: str
    details: Dict[str, Any]
    completed_at: str

# New Orchestration Events
class MissionLoadedEvent(BaseModel):
    mission_id: str
    user_id: str
    required_products: List[str]
    loaded_at: str

class VerificationCompletedEvent(BaseModel):
    mission_id: str
    cart_id: str
    score: int
    missing_items: List[str]
    completed_at: str

class CheckoutDecisionEvent(BaseModel):
    user_id: str
    cart_id: str
    allow_checkout: bool
    blocking_issues: List[str]
    decided_at: str

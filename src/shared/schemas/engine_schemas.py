from pydantic import BaseModel
from typing import List, Any

class VerificationRequest(BaseModel):
    missionId: str
    cartId: str

class VerificationResponseData(BaseModel):
    verification_score: int
    missing_items: List[str]

class RiskRequest(BaseModel):
    verification_score: int
    missing_items: List[str]

class RiskResponseData(BaseModel):
    compatibility_risk: str
    budget_risk: str
    quantity_risk: str
    timing_risk: str
    risk_score: int

class PreventionRequest(BaseModel):
    cartId: str

class PreventionResponseData(BaseModel):
    allow_checkout: bool
    reason: str

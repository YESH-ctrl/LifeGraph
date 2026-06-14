from pydantic import BaseModel
from typing import List, Any

class RiskRequest(BaseModel):
    verification_score: int
    missing_items: List[str]

class RiskResponseData(BaseModel):
    compatibility_risk: int
    budget_risk: int
    quantity_risk: int
    timing_risk: int
    risk_score: int

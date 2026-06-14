from pydantic import BaseModel
from typing import List, Any

class RiskRequest(BaseModel):
    verification_score: int
    missing_items: List[str]

class RiskResponseData(BaseModel):
    compatibility_risk: str
    budget_risk: str
    quantity_risk: str
    timing_risk: str
    risk_score: int

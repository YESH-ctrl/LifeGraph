from pydantic import BaseModel
from typing import List, Any, Optional

class RiskRisk(BaseModel):
    type: str
    severity: str
    reason: str

class RiskRequest(BaseModel):
    mission_id: str
    cart_products: List[str]
    total_cost: float
    budget: Optional[float]
    readiness_score: int
    critical_missing: List[str]
    missing_items: List[str]
    guest_count: int

class RiskResponseData(BaseModel):
    risk_score: int
    risk_level: str
    risks: List[RiskRisk]

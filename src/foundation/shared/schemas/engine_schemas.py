from pydantic import BaseModel
from typing import List, Any, Optional, Dict

class VerificationRequest(BaseModel):
    missionId: str
    cartId: str

class VerificationResponseData(BaseModel):
    verification_score: int
    missing_items: List[str]
    # V2 enriched fields
    critical_completion: float = 0.0
    important_completion: float = 0.0
    optional_completion: float = 0.0
    critical_missing: List[str] = []
    important_missing: List[str] = []
    optional_missing: List[str] = []
    recommended_products: List[str] = []

class RiskRequest(BaseModel):
    verification_score: int
    missing_items: List[str]
    # V2 enriched fields
    mission_id: str = ""
    cart_id: str = ""
    user_id: str = ""
    critical_completion: float = 0.0
    context: Optional[Dict[str, Any]] = None

class RiskResponseData(BaseModel):
    completion_risk: int = 0
    quantity_risk: int = 0
    compatibility_risk: int = 0
    timing_risk: int = 0
    budget_risk: int = 0
    risk_score: int = 0
    # Backward compat string fields (deprecated)
    compatibility_risk_label: str = "LOW"
    budget_risk_label: str = "LOW"
    quantity_risk_label: str = "LOW"
    timing_risk_label: str = "LOW"

class PreventionRequest(BaseModel):
    cartId: str
    missionId: str

class PreventionResponseData(BaseModel):
    allow_checkout: bool
    reason: str

class WorkflowCheckoutRequest(BaseModel):
    missionId: str
    cartId: str

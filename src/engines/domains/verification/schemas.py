from pydantic import BaseModel
from typing import List, Dict, Any

class VerificationRequest(BaseModel):
    mission_id: str
    cart_products: List[str]

class VerificationResponseData(BaseModel):
    readiness_score: int
    readiness_breakdown: Dict[str, int]
    required_items: List[str]
    missing_items: List[str]
    critical_missing: List[str]
    important_missing: List[str]
    optional_missing: List[str]
    recommended_products: List[str]

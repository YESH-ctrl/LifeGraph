from pydantic import BaseModel
from typing import List, Any

class VerificationRequest(BaseModel):
    missionId: str
    cartId: str

class VerificationResponseData(BaseModel):
    verification_score: int
    missing_items: List[str]
    readiness_score: int = 0
    recommended_additions: List[str] = []

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class MissionDiscoveryRequest(BaseModel):
    query: str


class IntentResult(BaseModel):
    intent: str
    entities: List[str] = []
    parameters: Dict[str, Any] = {}


class CandidateMission(BaseModel):
    mission: str
    score: float


class MissionResult(BaseModel):
    detected_mission: str
    confidence: float
    candidate_missions: List[CandidateMission]


class RequirementsResult(BaseModel):
    critical_products: List[str]
    important_products: List[str]
    optional_products: List[str]


class CartItem(BaseModel):
    product_id: str
    quantity: int
    reason: str


class MissionDiscoveryResponse(BaseModel):
    intent: IntentResult
    mission: MissionResult
    requirements: RequirementsResult
    suggested_cart: List[CartItem]
    explanation: List[str]

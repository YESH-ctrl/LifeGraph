from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MissionContext(BaseModel):
    budget: Optional[float] = None
    urgency: Optional[str] = None
    location: Optional[str] = None

class MissionExecutionRequest(BaseModel):
    userId: str
    missionId: str
    cartId: str
    context: Optional[MissionContext] = None

class MissionInfo(BaseModel):
    missionId: str
    name: str

class VerificationResult(BaseModel):
    score: int
    missingItems: List[str]

class RiskResult(BaseModel):
    overallRisk: str
    compatibilityRisk: int
    budgetRisk: int
    quantityRisk: int
    timingRisk: int

class SimulationResult(BaseModel):
    successProbability: int

class AdaptiveDecision(BaseModel):
    strictMode: bool

class CheckoutDecision(BaseModel):
    allowCheckout: bool
    blockingIssues: List[str]

class RecommendationItem(BaseModel):
    productId: str
    name: str
    price: float
    reason: str

class MissionExecutionResponse(BaseModel):
    mission: MissionInfo
    verification: VerificationResult
    risk: RiskResult
    simulation: SimulationResult
    adaptiveDecision: AdaptiveDecision
    checkout: CheckoutDecision
    recommendations: List[RecommendationItem] = []

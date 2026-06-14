from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MissionContext(BaseModel):
    budget: Optional[float] = None
    urgency: Optional[str] = None
    location: Optional[str] = None
    guest_count: Optional[int] = None
    event_date: Optional[str] = None

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
    criticalCompletion: float = 0.0
    importantCompletion: float = 0.0
    optionalCompletion: float = 0.0
    criticalMissing: List[str] = []
    importantMissing: List[str] = []
    optionalMissing: List[str] = []
    recommendedProducts: List[str] = []

class RiskResult(BaseModel):
    overallRisk: str
    completionRisk: int = 0
    quantityRisk: int = 0
    compatibilityRisk: int = 0
    budgetRisk: int = 0
    timingRisk: int = 0

class SimulationResult(BaseModel):
    successProbability: int
    requiredProducts: Dict[str, int] = {}
    availableProducts: Dict[str, int] = {}
    quantityGaps: Dict[str, int] = {}
    assumptions: List[str] = []

class AdaptiveDecision(BaseModel):
    strictMode: bool
    shopperType: str = ""
    recommendedIntervention: str = ""

class CheckoutDecision(BaseModel):
    allowCheckout: bool
    blockingIssues: List[str]
    reason: str = ""
    recommendedActions: List[str] = []
    riskSummary: Dict[str, int] = {}

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

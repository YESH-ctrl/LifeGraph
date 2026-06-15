from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Generic, TypeVar

T = TypeVar("T")

# --- GENERIC DECISION DELTA WRAPPER ---
class DecisionDelta(BaseModel, Generic[T]):
    original_output: Dict[str, Any] = Field(default_factory=dict, description="Deterministic engine output passed as input")
    ai_analysis: T = Field(description="Structured AI engine analysis output")
    recommended_changes: List[Dict[str, Any]] = Field(default_factory=list, description="AI recommended changes")
    accepted_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Changes approved and applied to the cart/scores")
    rejected_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Items or scores rejected by the agent")
    confidence: float = Field(default=1.0, description="Confidence score from 0.0 to 1.0")
    reasoning: List[str] = Field(default_factory=list, description="Reasoning steps and logs")

# --- MISSION AGENT ANALYSIS ---
class MissionAnalysisOutput(BaseModel):
    detected_mission: str = Field(description="The final detected mission ID")
    sub_goals: List[str] = Field(default_factory=list, description="Sub-goals like fat_loss, reduce_sugar")
    user_constraints: List[str] = Field(default_factory=list, description="User restrictions like diabetic, vegan, gluten-free")
    lifestyle_indicators: List[str] = Field(default_factory=list, description="Lifestyle indicators like healthy_eating, bulk_shopper")
    health_conditions: List[str] = Field(default_factory=list, description="Health conditions like diabetic, hypertensive")
    evidence_validation: List[Dict[str, str]] = Field(default_factory=list, description="Evidence mapping for constraints, health conditions, or lifestyle indicators")

# --- CART AGENT ANALYSIS ---
class CartItemFeedback(BaseModel):
    product_id: str
    title: str
    priority: str
    reason: str
    status: str = Field("APPROVED", description="APPROVED, QUESTIONABLE, or REJECTED")
    feedback: Optional[str] = None

class CartAnalysisOutput(BaseModel):
    items: List[CartItemFeedback] = Field(default_factory=list)
    mission_coherence_score: int = Field(description="Updated coherence score from 0 to 100")

# --- VERIFICATION AGENT ANALYSIS ---
class VerificationAnalysisOutput(BaseModel):
    readiness_score: int = Field(description="Adjusted readiness score")
    critical_missing: List[str] = Field(default_factory=list)
    important_missing: List[str] = Field(default_factory=list)
    recommended_products: List[str] = Field(default_factory=list)

# --- RISK AGENT ANALYSIS ---
class RiskAnalysisOutput(BaseModel):
    risk_score: int
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    risks: List[Dict[str, Any]] = Field(default_factory=list)

# --- REGRET PREVENTION AGENT ANALYSIS ---
class RegretAnalysisOutput(BaseModel):
    forgotten_items: List[str] = Field(default_factory=list)
    impact_score: int

# --- SIMULATION AGENT ANALYSIS ---
class SimulationAnalysisOutput(BaseModel):
    current_success: int
    optimized_success: int
    improvement: int
    recommended_additions: List[str] = Field(default_factory=list)

# --- AUDITOR AGENT ANALYSIS ---
class AuditFailure(BaseModel):
    type: str  # UUID_LEAK, CATEGORY_MISMATCH, COHERENCE_VIOLATION, HALLUCINATION
    message: str
    severity: str  # HIGH, MEDIUM, LOW

class AuditorAnalysisOutput(BaseModel):
    overall_confidence_score: float = Field(description="Final aggregated confidence score from 0.0 to 1.0")
    audit_score: int = Field(description="Compliance audit score from 0 to 100")
    grounding_score: int = Field(default=100, description="Audit grounding score from 0 to 100")
    consistency_score: int = Field(default=100, description="Audit consistency score from 0 to 100")
    failures: List[AuditFailure] = Field(default_factory=list)
    warnings: List[AuditFailure] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)

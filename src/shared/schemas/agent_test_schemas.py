from pydantic import BaseModel
from typing import List, Dict, Any

class MissionDetectionTestRequest(BaseModel):
    query: str

class CandidateMissionScore(BaseModel):
    mission: str
    score: float

class MissionDetectionTestResponse(BaseModel):
    detected_mission: str
    confidence: float
    candidate_missions: List[CandidateMissionScore]
    parameters: Dict[str, Any]

class VerificationTestRequest(BaseModel):
    mission_id: str
    products: List[str]

class VerificationTestResponse(BaseModel):
    readiness_score: int
    required_items: List[str]
    missing_items: List[str]

class RiskTestRequest(BaseModel):
    mission_id: str
    products: List[str]

class RiskTestResponse(BaseModel):
    completion_risk: int
    quantity_risk: int
    compatibility_risk: int
    overall_risk: int

class SimulatorProductInput(BaseModel):
    product: str
    quantity: int

class SimulatorTestRequest(BaseModel):
    mission_id: str
    guest_count: int
    products: List[SimulatorProductInput]

class SimulatorTestResponse(BaseModel):
    success_probability: float
    warnings: List[str]

class PreventionTestRequest(BaseModel):
    products: List[str]

class PreventionTestResponse(BaseModel):
    checkout_allowed: bool
    missing_dependencies: List[str]

class MemoryTestRequest(BaseModel):
    user_id: str

class MemoryTestResponse(BaseModel):
    active_missions: List[str]
    completed_missions: List[str]

class AdaptiveTestRequest(BaseModel):
    user_id: str

class AdaptiveTestResponse(BaseModel):
    shopper_type: str
    recommended_intervention: str

class GraphRelation(BaseModel):
    source: str
    target: str

class GraphMissionResponse(BaseModel):
    mission: str
    required: List[str]
    optional: List[str]
    dependencies: List[GraphRelation]
    substitutions: List[GraphRelation]
    compatibility: List[GraphRelation]

class OrchestratorTestRequest(BaseModel):
    query: str

class OrchestratorTestResponse(BaseModel):
    mission_detection: Dict[str, Any]
    verification: Dict[str, Any]
    risk: Dict[str, Any]
    simulation: Dict[str, Any]
    prevention: Dict[str, Any]
    adaptive: Dict[str, Any]
    memory: Dict[str, Any]
    final_decision: Dict[str, Any]

class SystemStatusResponse(BaseModel):
    missions: int
    products: int
    relationships: int
    embedding_model: str
    reranker_model: str
    orchestrator_status: str

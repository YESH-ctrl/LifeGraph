from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MissionDetectionRequest(BaseModel):
    text: str

class CandidateMission(BaseModel):
    mission_id: str
    final_score: float
    intent_score: float
    embedding_score: float
    keyword_score: float
    graph_score: float
    matched_keywords: List[str]
    matched_intents: List[str]

class MissionDetectionResponse(BaseModel):
    detected_mission: str
    confidence: float
    candidate_missions: List[CandidateMission]
    parameters: Dict[str, Any]
    why_detected: Dict[str, Any]
    score_breakdown: Dict[str, float]
    matched_keywords: List[str]
    matched_intents: List[str]

class QueryAnalysisResponse(BaseModel):
    tokens: List[str]
    matched_keywords: Dict[str, List[str]]
    matched_synonyms: Dict[str, List[str]]
    matched_intents: Dict[str, List[str]]
    matched_missions: List[str]
    extracted_parameters: Dict[str, Any]

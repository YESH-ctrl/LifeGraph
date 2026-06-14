from pydantic import BaseModel
from typing import List, Optional

class DependencyMapping(BaseModel):
    source: str
    target: str

class CompatibilityMapping(BaseModel):
    source: str
    target: str

class SubstitutionMapping(BaseModel):
    source: str
    target: str

class ConsumptionRule(BaseModel):
    product: str
    unit: str
    serves_per_unit: float

class MissionSeedRequest(BaseModel):
    mission_id: str
    name: str
    description: str
    category: str
    
    required: List[str]
    optional: Optional[List[str]] = []
    
    dependencies: Optional[List[DependencyMapping]] = []
    compatibility: Optional[List[CompatibilityMapping]] = []
    substitutions: Optional[List[SubstitutionMapping]] = []
    
    keywords: Optional[List[str]] = []
    synonyms: Optional[List[str]] = []
    intent_examples: Optional[List[str]] = []
    embedding: Optional[List[float]] = []
    consumption_rules: Optional[List[ConsumptionRule]] = []

class BulkMissionSeedRequest(BaseModel):
    missions: List[MissionSeedRequest]

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CartGenerationRequest(BaseModel):
    mission_id: str
    parameters: Dict[str, Any]

class CartProduct(BaseModel):
    product_id: str
    title: str
    quantity: int
    priority: str
    estimated_cost: float
    reason: Optional[str] = None

class Substitution(BaseModel):
    product: str
    alternatives: List[str]

class CartGenerationResponse(BaseModel):
    mission_id: str
    required_products: List[CartProduct]
    optional_products: List[CartProduct]
    estimated_total_cost: float
    estimated_serving_capacity: int
    graph_coverage: int
    reasoning: List[str]
    substitutions: List[Substitution]
    mission_coherence_score: Optional[int] = None

from pydantic import BaseModel
from typing import List

class RegretPreventionRequest(BaseModel):
    mission_id: str
    cart_products: List[str]

class RegretPreventionResponseData(BaseModel):
    forgotten_items: List[str]
    impact_score: int

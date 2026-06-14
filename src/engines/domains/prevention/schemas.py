from pydantic import BaseModel
from typing import List

class PreventionRequest(BaseModel):
    cartId: str
    missionId: str

class PreventionResponseData(BaseModel):
    allow_checkout: bool
    reason: str

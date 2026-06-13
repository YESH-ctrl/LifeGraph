from pydantic import BaseModel
from typing import List

class PreventionRequest(BaseModel):
    cartId: str

class PreventionResponseData(BaseModel):
    allow_checkout: bool
    reason: str

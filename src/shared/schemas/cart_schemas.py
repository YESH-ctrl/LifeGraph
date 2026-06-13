from typing import List
from pydantic import BaseModel, Field

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

class CartCreate(BaseModel):
    user_id: str

class CartUpdate(BaseModel):
    user_id: str | None = None
    status: str | None = None

class CartAddItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

class CartResponse(BaseModel):
    id: str
    user_id: str
    status: str
    total: float
    items: List[CartItem] = []

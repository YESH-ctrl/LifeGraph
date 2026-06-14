from pydantic import BaseModel, Field

from typing import List

class ProductBase(BaseModel):
    name: str
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    category: str
    subcategory: str | None = None
    semanticTags: List[str] | None = None
    missionHints: List[dict] | None = None
    embeddingText: str | None = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)
    category: str | None = None

class ProductResponse(ProductBase):
    id: str

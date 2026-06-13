from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category: str

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category: str | None = None

class ProductResponse(ProductBase):
    id: str

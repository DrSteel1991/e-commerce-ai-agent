from decimal import Decimal

from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Decimal
    stock: int
    category: str | None = None

    class Config:
        from_attributes = True

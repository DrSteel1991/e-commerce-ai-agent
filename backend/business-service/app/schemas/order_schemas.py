from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: int
    customer_id: int | None = None
    total_price: Decimal
    status: str
    ordered_at: datetime | None = None

    class Config:
        from_attributes = True

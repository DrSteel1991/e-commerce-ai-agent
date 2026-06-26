from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderSummaryResponse(BaseModel):
    order_id: int
    customer_id: int | None = None
    status: str
    total_price: Decimal
    ordered_at: datetime | None = None
    message: str

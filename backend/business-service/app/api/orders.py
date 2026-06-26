from app.domain.services.order_service import (
    find_order,
    get_order_summary,
    list_orders_by_status,
)
from app.infrastructure.database.database import get_db
from app.schemas.order_schemas import OrderResponse
from app.schemas.order_summary_schemas import OrderSummaryResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/status/{status}", response_model=list[OrderResponse])
def get_orders_by_status(status: str, limit: int = 20, db: Session = Depends(get_db)):
    return list_orders_by_status(db, status, limit)


@router.get("/{order_id}/summary", response_model=OrderSummaryResponse)
def order_summary(order_id: int, db: Session = Depends(get_db)):
    summary = get_order_summary(db, order_id)

    if not summary:
        raise HTTPException(status_code=404, detail="Order not found")

    return summary


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = find_order(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

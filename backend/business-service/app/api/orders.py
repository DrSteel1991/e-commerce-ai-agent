from app.domain.services.order_service import (
    OrderAccessError,
    find_order,
    get_order_summary,
    list_orders_by_status,
)
from app.infrastructure.database.database import get_db
from app.schemas.order_schemas import OrderResponse
from app.schemas.order_summary_schemas import OrderSummaryResponse
from ecommerce_contracts import USER_ID_HEADER
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/orders", tags=["Orders"])


def _handle_order_access_error(exc: OrderAccessError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.get("/status/{status}", response_model=list[OrderResponse])
def get_orders_by_status(status: str, limit: int = 20, db: Session = Depends(get_db)):
    return list_orders_by_status(db, status, limit)


@router.get("/{order_id}/summary", response_model=OrderSummaryResponse)
def order_summary(
    order_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Header(None, alias=USER_ID_HEADER),
):
    try:
        return get_order_summary(db, order_id, user_id=user_id)
    except OrderAccessError as exc:
        _handle_order_access_error(exc)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user_id: str | None = Header(None, alias=USER_ID_HEADER),
):
    try:
        return find_order(db, order_id, user_id=user_id)
    except OrderAccessError as exc:
        _handle_order_access_error(exc)

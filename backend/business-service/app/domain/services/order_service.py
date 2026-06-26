from app.domain.repositories.order_repository import (
    get_order_by_id,
    get_orders_by_status,
)
from sqlalchemy.orm import Session


def find_order(db: Session, order_id: int):
    return get_order_by_id(db, order_id)


def list_orders_by_status(db: Session, status: str, limit: int = 20):
    return get_orders_by_status(db=db, status=status, limit=limit)


def get_order_summary(db: Session, order_id: int):
    order = get_order_by_id(db, order_id)

    if not order:
        return None

    message = (
        f"Order #{order.id} is currently {order.status}. "
        f"The total price is {order.total_price}."
    )

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "total_price": order.total_price,
        "ordered_at": order.ordered_at,
        "message": message,
    }

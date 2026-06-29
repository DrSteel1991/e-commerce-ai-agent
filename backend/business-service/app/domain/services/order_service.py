from uuid import UUID

from app.domain.repositories.customer_repository import get_customer_by_user_id
from app.domain.repositories.order_repository import (
    get_order_by_id,
    get_orders_by_status,
)
from sqlalchemy.orm import Session


class OrderAccessError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


def _verify_order_access(db: Session, order_id: int, user_id: str):
    customer = get_customer_by_user_id(db, UUID(user_id))

    if not customer:
        raise OrderAccessError(404, "Customer profile not found for this user")

    order = get_order_by_id(db, order_id)

    if not order:
        raise OrderAccessError(404, "Order not found")

    if order.customer_id != customer.id:
        raise OrderAccessError(403, "You do not have access to this order")

    return order


def find_order(db: Session, order_id: int, user_id: str | None = None):
    if user_id is None:
        raise OrderAccessError(401, "Authentication required to view orders")

    return _verify_order_access(db, order_id, user_id)


def list_orders_by_status(db: Session, status: str, limit: int = 20):
    return get_orders_by_status(db=db, status=status, limit=limit)


def get_order_summary(db: Session, order_id: int, user_id: str | None = None):
    order = find_order(db, order_id, user_id)

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

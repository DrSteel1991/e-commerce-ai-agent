from app.infrastructure.database.models.order_model import Order
from sqlalchemy.orm import Session


def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders_by_status(db: Session, status: str, limit: int = 20):
    return (
        db.query(Order)
        .filter(Order.status == status)
        .order_by(Order.ordered_at.desc())
        .limit(limit)
        .all()
    )

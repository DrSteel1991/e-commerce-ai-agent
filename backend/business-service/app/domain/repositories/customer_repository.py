from uuid import UUID

from app.infrastructure.database.models.customer_model import Customer
from sqlalchemy.orm import Session


def get_customer_by_user_id(db: Session, user_id: UUID | str):
    return db.query(Customer).filter(Customer.user_id == user_id).first()

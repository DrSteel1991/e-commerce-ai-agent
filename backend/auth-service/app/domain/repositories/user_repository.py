from sqlalchemy.orm import Session

from app.infrastructure.database.models.user_model import User


def get_active_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).filter(User.is_active).first()


def get_active_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).filter(User.is_active).first()

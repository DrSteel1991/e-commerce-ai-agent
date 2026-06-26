from sqlalchemy import text
from sqlalchemy.orm import Session


def get_active_user_by_email(db: Session, email: str):
    query = text("""
        SELECT id, email, full_name, password_hash
        FROM users
        WHERE email = :email
        AND is_active = TRUE
    """)

    return db.execute(query, {"email": email}).fetchone()


def get_active_user_by_id(db: Session, user_id: str):
    query = text("""
        SELECT id, email, full_name
        FROM users
        WHERE id = :user_id
        AND is_active = TRUE
    """)

    return db.execute(query, {"user_id": user_id}).fetchone()

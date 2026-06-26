from sqlalchemy.orm import Session

from app.domain.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserNotFoundException,
)
from app.domain.repositories.user_repository import (
    get_active_user_by_email,
    get_active_user_by_id,
)
from app.infrastructure.security.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)


def login(db: Session, email: str, password: str):
    user = get_active_user_by_email(db, email)

    if not user:
        raise InvalidCredentialsException()

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsException()

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
        }
    )

    return token


def get_current_user(db: Session, token: str):
    payload = decode_access_token(token)

    if not payload:
        raise InvalidTokenException()

    user = get_active_user_by_id(db, payload["sub"])

    if not user:
        raise UserNotFoundException()

    return user

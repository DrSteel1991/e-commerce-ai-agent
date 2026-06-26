from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.domain.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserNotFoundException,
)
from app.domain.services.auth_service import (
    get_current_user as get_current_user_service,
)
from app.domain.services.auth_service import login as login_service
from app.infrastructure.database.database import get_db
from app.schemas.auth_schemas import CurrentUserResponse, LoginRequest, TokenResponse

router = APIRouter(tags=["Auth"])
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        access_token = login_service(
            db=db, email=request.email, password=request.password
        )

        return TokenResponse(access_token=access_token)

    except InvalidCredentialsException:
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        user = get_current_user_service(db=db, token=credentials.credentials)

        return CurrentUserResponse(
            id=user.id, email=user.email, full_name=user.full_name
        )

    except InvalidTokenException:
        raise HTTPException(status_code=401, detail="Invalid token")

    except UserNotFoundException:
        raise HTTPException(status_code=401, detail="User not found")

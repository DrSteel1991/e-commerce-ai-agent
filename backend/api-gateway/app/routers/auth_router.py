import httpx
from ecommerce_contracts import LoginRequest
from fastapi import APIRouter, Header, HTTPException

from app.services.auth_client import get_current_user, login

router = APIRouter()


@router.post("/login")
async def login_user(request: LoginRequest):
    try:
        return await login(email=request.email, password=request.password)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.json().get("detail", "Login failed"),
        ) from exc


@router.get("/me")
async def me(authorization: str = Header(..., alias="Authorization")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.removeprefix("Bearer ").strip()

    try:
        return await get_current_user(token)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.json().get("detail", "Unauthorized"),
        ) from exc

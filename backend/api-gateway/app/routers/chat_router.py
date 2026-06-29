import httpx
from ecommerce_contracts import ChatRequest
from fastapi import APIRouter, Header, HTTPException

from app.services.agent_client import send_message_to_agent
from app.services.auth_client import get_current_user

router = APIRouter()


@router.post("")
async def chat(
    request: ChatRequest,
    authorization: str | None = Header(None, alias="Authorization"),
):
    user_id: str | None = None

    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization.removeprefix("Bearer ").strip()

        try:
            user = await get_current_user(token)
            user_id = str(user["id"])
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=exc.response.json().get("detail", "Invalid or expired token"),
            ) from exc

    try:
        return await send_message_to_agent(
            message=request.message,
            user_id=user_id,
            session_id=request.session_id,
        )
    except httpx.HTTPStatusError as exc:
        detail = "Agent service error"
        try:
            detail = exc.response.json().get("detail", detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Agent service is unavailable",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.agent_client import send_message_to_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None


@router.post("")
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        return await send_message_to_agent(
            message=request.message,
            user_id=request.user_id,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Agent service error",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Agent service is unavailable",
        ) from exc

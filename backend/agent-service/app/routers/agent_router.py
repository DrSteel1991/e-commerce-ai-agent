from fastapi import APIRouter
from pydantic import BaseModel

from app.domain.services.agent_orchestrator import handle_message

router = APIRouter()


class AgentChatRequest(BaseModel):
    message: str
    user_id: str | None = None


@router.post("/chat")
async def chat(request: AgentChatRequest):
    return await handle_message(
        message=request.message,
        user_id=request.user_id,
    )

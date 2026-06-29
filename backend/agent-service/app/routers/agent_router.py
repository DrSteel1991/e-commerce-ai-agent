from ecommerce_contracts import USER_ID_HEADER, ChatRequest, require_internal_api_key
from fastapi import APIRouter, Depends, Header

from app.domain.services.agent_orchestrator import handle_message

router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    _: None = Depends(require_internal_api_key),
    user_id: str | None = Header(None, alias=USER_ID_HEADER),
):
    return await handle_message(message=request.message, user_id=user_id)

import logging

from app.domain.agents.langgraph_agent import run_tool_agent
from app.domain.services.conversation_service import (
    append_message,
    ensure_session_id,
    get_history,
)
from app.infrastructure.llm.openai_client import is_llm_available
from openai import APIConnectionError, AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)


def _configuration_error_response(user_id: str | None) -> dict:
    return {
        "answer": (
            "The assistant is not configured. "
            "Set OPENAI_API_KEY in backend/agent-service/.env and restart the service."
        ),
        "sources": [],
        "agent_action": "configuration_error",
        "intent": "general",
        "user_id": user_id,
        "data": None,
    }


def _agent_error_response(user_id: str | None, *, detail: str | None = None) -> dict:
    answer = detail or (
        "Something went wrong while processing your request. "
        "Please try again shortly."
    )
    return {
        "answer": answer,
        "sources": [],
        "agent_action": "agent_error",
        "intent": "general",
        "user_id": user_id,
        "data": None,
    }


def _map_openai_error(exc: Exception) -> str | None:
    if isinstance(exc, AuthenticationError):
        return (
            "The OpenAI API key is invalid or expired. "
            "Update OPENAI_API_KEY in backend/agent-service/.env and restart the agent."
        )
    if isinstance(exc, RateLimitError):
        return "OpenAI rate limit reached. Please wait a moment and try again."
    if isinstance(exc, APIConnectionError):
        return "Could not reach the OpenAI API. Check your network connection."
    return None


async def handle_message(
    message: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    """
    Agent entry point: LangGraph tool-calling loop with conversation memory.
    """
    session_id = ensure_session_id(session_id)
    history = get_history(session_id)

    if not is_llm_available():
        response = _configuration_error_response(user_id)
    else:
        try:
            response = await run_tool_agent(
                message, user_id=user_id, history=history
            )
        except Exception as exc:
            logger.exception("Tool agent failed")
            response = _agent_error_response(
                user_id, detail=_map_openai_error(exc)
            )

    response["session_id"] = session_id
    append_message(session_id, "user", message)
    append_message(session_id, "assistant", response.get("answer", ""))

    return response

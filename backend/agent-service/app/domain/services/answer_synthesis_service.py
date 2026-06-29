import asyncio
import json
import logging

from app.infrastructure.llm.openai_client import chat_completion, is_llm_available

logger = logging.getLogger(__name__)

SYNTHESIS_SYSTEM_PROMPT = """You are a friendly e-commerce customer support assistant.

Write a concise, natural reply for the customer using ONLY the provided tool data.
Do not invent order numbers, prices, stock levels, or policies that are not in the data.
If data is missing, say what you still need from the customer.
Keep answers to 2-4 short sentences unless listing products."""


def _format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return "No prior messages."

    lines = [f"{item['role']}: {item['content']}" for item in history[-6:]]
    return "\n".join(lines)


def _synthesize_with_llm(
    message: str,
    intent: str,
    data: dict,
    history: list[dict[str, str]],
) -> str:
    return chat_completion(
        [
            {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Conversation history:\n{_format_history(history)}\n\n"
                    f"Customer message: {message}\n"
                    f"Detected intent: {intent}\n"
                    f"Tool data JSON:\n{json.dumps(data, default=str)}"
                ),
            },
        ],
        temperature=0.2,
    )


async def synthesize_business_answer(
    message: str,
    intent: str,
    data: dict,
    history: list[dict[str, str]] | None = None,
    *,
    fallback: str,
) -> str:
    history = history or []

    if not is_llm_available():
        return fallback

    try:
        return await asyncio.to_thread(
            _synthesize_with_llm, message, intent, data, history
        )
    except Exception:
        logger.exception("LLM answer synthesis failed; using fallback text")
        return fallback


def build_contextual_question(message: str, history: list[dict[str, str]]) -> str:
    """Add recent conversation context before sending a question to RAG."""
    if not history:
        return message

    return (
        f"Conversation context:\n{_format_history(history)}\n\n"
        f"Current customer question: {message}"
    )

import asyncio
import logging

from app.domain.intents import Intent
from app.domain.services.intent_service import IntentResult, detect_intent_keywords
from app.infrastructure.llm.openai_client import chat_completion_json, is_llm_available

logger = logging.getLogger(__name__)

VALID_INTENTS = [intent.value for intent in Intent]

INTENT_SYSTEM_PROMPT = f"""You classify customer support messages for an e-commerce store.

Return JSON with exactly these fields:
- intent: one of {VALID_INTENTS}
- order_id: integer order number if mentioned or implied by recent conversation, else null
- search_query: short product search phrase for product_info intent, else null

Rules:
- Use conversation history to resolve follow-ups like "what about order 2?" or "can I return it?"
- order_status: tracking, delivery status, "where is my order"
- refund_policy: returns, refunds, money back
- shipping_policy: shipping times, delivery options, shipping costs
- payment_policy: payment methods, billing, promo codes
- faq: account help, password, general how-to questions
- product_info: product availability, price, stock, categories
- general: anything else policy-related without a clearer category
"""


def _format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return "No prior messages."

    lines = [f"{item['role']}: {item['content']}" for item in history[-8:]]
    return "\n".join(lines)


def _parse_intent_payload(payload: dict) -> IntentResult:
    raw_intent = payload.get("intent", Intent.GENERAL.value)
    intent = Intent.GENERAL

    try:
        intent = Intent(raw_intent)
    except ValueError:
        logger.warning("Unknown intent from LLM: %s", raw_intent)

    order_id = payload.get("order_id")
    if order_id is not None:
        try:
            order_id = int(order_id)
        except (TypeError, ValueError):
            order_id = None

    search_query = payload.get("search_query")
    if isinstance(search_query, str):
        search_query = search_query.strip() or None
    else:
        search_query = None

    return IntentResult(
        intent=intent,
        order_id=order_id,
        search_query=search_query,
    )


def _detect_intent_with_llm(message: str, history: list[dict[str, str]]) -> IntentResult:
    payload = chat_completion_json(
        [
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Conversation history:\n{_format_history(history)}\n\n"
                    f"Latest customer message:\n{message}"
                ),
            },
        ]
    )
    return _parse_intent_payload(payload)


async def detect_intent(
    message: str, history: list[dict[str, str]] | None = None
) -> IntentResult:
    """
    Classify intent with OpenAI, falling back to keyword rules if the LLM fails.
    """
    history = history or []

    if not is_llm_available():
        return detect_intent_keywords(message)

    try:
        return await asyncio.to_thread(_detect_intent_with_llm, message, history)
    except Exception:
        logger.exception("LLM intent detection failed; using keyword fallback")
        return detect_intent_keywords(message)

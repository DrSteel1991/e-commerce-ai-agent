import logging
import os

from dotenv import load_dotenv

from app.domain.agents.langgraph_agent import run_tool_agent
from app.domain.intents import Intent
from app.domain.services.answer_synthesis_service import (
    build_contextual_question,
    synthesize_business_answer,
)
from app.domain.services.conversation_service import (
    append_message,
    ensure_session_id,
    get_history,
)
from app.domain.services.intent_service import IntentResult
from app.domain.services.llm_intent_service import detect_intent
from app.domain.services.product_query import extract_product_search_query
from app.infrastructure.llm.openai_client import is_llm_available
from app.services.business_client import get_order_summary, list_products, search_products
from app.services.rag_client import ask_rag_service
from ecommerce_contracts.errors import ServiceError

_ = load_dotenv()

logger = logging.getLogger(__name__)

USE_TOOL_AGENT = os.environ.get("AGENT_MODE", "tool_calling").lower() != "legacy"


async def handle_message(
    message: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    """
    Agent entry point.

    - tool_calling mode (default): LangGraph + LLM tool calling when OPENAI_API_KEY is set
    - legacy mode or no API key: keyword/intent router from the original implementation
    """
    session_id = ensure_session_id(session_id)
    history = get_history(session_id)

    if USE_TOOL_AGENT and is_llm_available():
        try:
            response = await run_tool_agent(
                message, user_id=user_id, history=history
            )
        except Exception:
            logger.exception("Tool agent failed; falling back to legacy router")
            response = await _handle_message_legacy(message, user_id, history)
    else:
        response = await _handle_message_legacy(message, user_id, history)

    response["session_id"] = session_id
    append_message(session_id, "user", message)
    append_message(session_id, "assistant", response.get("answer", ""))

    return response


async def _handle_message_legacy(
    message: str,
    user_id: str | None,
    history: list[dict[str, str]],
) -> dict:
    """Original intent-router implementation (fallback without OpenAI)."""
    intent_result = await detect_intent(message, history)

    try:
        if intent_result.intent == Intent.ORDER_STATUS:
            response = await _handle_order_status(
                message, intent_result, user_id, history
            )
        elif intent_result.intent == Intent.REFUND_POLICY:
            response = await _handle_knowledge_base(
                message,
                user_id,
                Intent.REFUND_POLICY,
                "used_rag_refund_policy",
                history,
            )
        elif intent_result.intent == Intent.SHIPPING_POLICY:
            response = await _handle_knowledge_base(
                message,
                user_id,
                Intent.SHIPPING_POLICY,
                "used_rag_shipping_policy",
                history,
            )
        elif intent_result.intent == Intent.PAYMENT_POLICY:
            response = await _handle_knowledge_base(
                message,
                user_id,
                Intent.PAYMENT_POLICY,
                "used_rag_payment_policy",
                history,
            )
        elif intent_result.intent == Intent.FAQ:
            response = await _handle_knowledge_base(
                message, user_id, Intent.FAQ, "used_rag_faq", history
            )
        elif intent_result.intent == Intent.PRODUCT_INFO:
            response = await _handle_product_info(
                message, intent_result, user_id, history
            )
        else:
            response = await _handle_general(message, user_id, history)
    except ServiceError as exc:
        response = {
            "answer": exc.user_message,
            "sources": [],
            "agent_action": "service_error",
            "intent": intent_result.intent.value,
            "user_id": user_id,
        }
    except Exception:
        logger.exception("Unhandled agent error")
        response = {
            "answer": (
                "Something went wrong while processing your request. "
                "Please try again shortly."
            ),
            "sources": [],
            "agent_action": "unhandled_error",
            "intent": intent_result.intent.value,
            "user_id": user_id,
        }

    return response


_BROWSE_PATTERNS = (
    "list",
    "show me",
    "what do you sell",
    "what products",
    "catalog",
    "browse",
    "all products",
    "products you have",
    "what do you have",
)


def _is_browse_request(message: str, search_query: str | None) -> bool:
    text = message.lower()
    if search_query and search_query.lower() != text:
        return False
    return any(pattern in text for pattern in _BROWSE_PATTERNS)


async def _handle_order_status(
    message: str,
    intent_result: IntentResult,
    user_id: str | None,
    history: list[dict[str, str]],
) -> dict:
    if intent_result.order_id is None:
        return {
            "answer": (
                "I can help you check your order. "
                "Please share your order number, for example: order 42."
            ),
            "sources": [],
            "agent_action": "asked_for_order_id",
            "intent": Intent.ORDER_STATUS.value,
            "user_id": user_id,
        }

    if user_id is None:
        return {
            "answer": "Please sign in to check your order status.",
            "sources": [],
            "agent_action": "auth_required",
            "intent": Intent.ORDER_STATUS.value,
            "user_id": user_id,
        }

    summary = await get_order_summary(intent_result.order_id, user_id)

    if summary is None:
        return {
            "answer": f"I could not find order #{intent_result.order_id}.",
            "sources": [],
            "agent_action": "order_not_found",
            "intent": Intent.ORDER_STATUS.value,
            "user_id": user_id,
            "data": {"order_id": intent_result.order_id},
        }

    fallback = summary["message"]
    answer = await synthesize_business_answer(
        message,
        Intent.ORDER_STATUS.value,
        summary,
        history,
        fallback=fallback,
    )

    return {
        "answer": answer,
        "sources": [],
        "agent_action": "used_business_service_llm",
        "intent": Intent.ORDER_STATUS.value,
        "user_id": user_id,
        "data": summary,
    }


async def _handle_knowledge_base(
    message: str,
    user_id: str | None,
    intent: Intent,
    agent_action: str,
    history: list[dict[str, str]],
) -> dict:
    contextual_question = build_contextual_question(message, history)
    rag_response = await ask_rag_service(contextual_question)

    return {
        "answer": rag_response.get("answer"),
        "sources": rag_response.get("sources", []),
        "agent_action": agent_action,
        "intent": intent.value,
        "user_id": user_id,
    }


async def _handle_product_info(
    message: str,
    intent_result: IntentResult,
    user_id: str | None,
    history: list[dict[str, str]],
) -> dict:
    if _is_browse_request(message, intent_result.search_query):
        products = await list_products(limit=10)
        query = None
    else:
        raw_query = intent_result.search_query or message
        query = extract_product_search_query(raw_query)
        products = await search_products(query)

    if not products:
        return {
            "answer": "I could not find any matching products right now.",
            "sources": [],
            "agent_action": "used_business_service",
            "intent": Intent.PRODUCT_INFO.value,
            "user_id": user_id,
            "data": {"products": [], "search_query": query},
        }

    product_data = {"products": products[:5], "search_query": query}
    if len(products) == 1:
        product = products[0]
        fallback = (
            f"{product['name']} costs ${product['price']} "
            f"({product['stock']} in stock)."
        )
    else:
        lines = [
            f"- {product['name']} (${product['price']}) — {product['stock']} in stock"
            for product in products[:5]
        ]
        fallback = "Here are some products I found:\n" + "\n".join(lines)

    answer = await synthesize_business_answer(
        message,
        Intent.PRODUCT_INFO.value,
        product_data,
        history,
        fallback=fallback,
    )

    return {
        "answer": answer,
        "sources": [],
        "agent_action": "used_business_service_llm",
        "intent": Intent.PRODUCT_INFO.value,
        "user_id": user_id,
        "data": product_data,
    }


async def _handle_general(
    message: str, user_id: str | None, history: list[dict[str, str]]
) -> dict:
    return await _handle_knowledge_base(
        message, user_id, Intent.GENERAL, "used_rag_general", history
    )

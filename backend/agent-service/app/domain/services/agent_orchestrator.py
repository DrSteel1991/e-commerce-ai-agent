from app.domain.intents import Intent
from app.domain.services.intent_service import IntentResult, detect_intent
from app.services.business_client import get_order_summary, search_products
from app.services.rag_client import ask_rag_service
from ecommerce_contracts.errors import ServiceError


async def handle_message(message: str, user_id: str | None = None) -> dict:
    """
    The agent brain:
    1. Detect what the user wants
    2. Call the right backend service
    3. Return a unified response
    """
    intent_result = detect_intent(message)

    try:
        if intent_result.intent == Intent.ORDER_STATUS:
            return await _handle_order_status(intent_result, user_id)

        if intent_result.intent == Intent.REFUND_POLICY:
            return await _handle_knowledge_base(
                message, user_id, Intent.REFUND_POLICY, "used_rag_refund_policy"
            )

        if intent_result.intent == Intent.SHIPPING_POLICY:
            return await _handle_knowledge_base(
                message, user_id, Intent.SHIPPING_POLICY, "used_rag_shipping_policy"
            )

        if intent_result.intent == Intent.PAYMENT_POLICY:
            return await _handle_knowledge_base(
                message, user_id, Intent.PAYMENT_POLICY, "used_rag_payment_policy"
            )

        if intent_result.intent == Intent.FAQ:
            return await _handle_knowledge_base(
                message, user_id, Intent.FAQ, "used_rag_faq"
            )

        if intent_result.intent == Intent.PRODUCT_INFO:
            return await _handle_product_info(message, user_id)

        return await _handle_general(message, user_id)
    except ServiceError as exc:
        return {
            "answer": exc.user_message,
            "sources": [],
            "agent_action": "service_error",
            "intent": intent_result.intent.value,
            "user_id": user_id,
        }


async def _handle_order_status(
    intent_result: IntentResult, user_id: str | None
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

    return {
        "answer": summary["message"],
        "sources": [],
        "agent_action": "used_business_service",
        "intent": Intent.ORDER_STATUS.value,
        "user_id": user_id,
        "data": summary,
    }


async def _handle_knowledge_base(
    message: str, user_id: str | None, intent: Intent, agent_action: str
) -> dict:
    rag_response = await ask_rag_service(message)

    return {
        "answer": rag_response.get("answer"),
        "sources": rag_response.get("sources", []),
        "agent_action": agent_action,
        "intent": intent.value,
        "user_id": user_id,
    }


async def _handle_product_info(message: str, user_id: str | None) -> dict:
    products = await search_products(message)

    if not products:
        return {
            "answer": "I could not find any matching products right now.",
            "sources": [],
            "agent_action": "used_business_service",
            "intent": Intent.PRODUCT_INFO.value,
            "user_id": user_id,
            "data": {"products": []},
        }

    lines = [
        f"- {product['name']} (${product['price']}) — {product['stock']} in stock"
        for product in products[:5]
    ]

    return {
        "answer": "Here are some products I found:\n" + "\n".join(lines),
        "sources": [],
        "agent_action": "used_business_service",
        "intent": Intent.PRODUCT_INFO.value,
        "user_id": user_id,
        "data": {"products": products},
    }


async def _handle_general(message: str, user_id: str | None) -> dict:
    return await _handle_knowledge_base(
        message, user_id, Intent.GENERAL, "used_rag_general"
    )

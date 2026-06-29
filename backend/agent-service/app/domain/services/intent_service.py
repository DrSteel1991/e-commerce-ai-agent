import re

from app.domain.intents import Intent


class IntentResult:
    def __init__(self, intent: Intent, order_id: int | None = None):
        self.intent = intent
        self.order_id = order_id


ORDER_KEYWORDS = [
    "where is my order",
    "track my order",
    "order status",
    "status of order",
    "when will my order arrive",
    "shipping status",
]

SHIPPING_POLICY_KEYWORDS = [
    "shipping policy",
    "delivery policy",
    "how long does shipping",
    "how long does delivery",
    "free shipping",
    "express shipping",
    "international shipping",
    "delivery time",
    "when will it arrive",
    "shipping cost",
    "shipping fee",
]

PAYMENT_KEYWORDS = [
    "payment method",
    "pay with",
    "credit card",
    "paypal",
    "cash on delivery",
    "cod",
    "billing",
    "invoice",
    "promo code",
]

FAQ_KEYWORDS = [
    "faq",
    "frequently asked",
    "how do i create an account",
    "forgot my password",
    "price match",
    "restock",
    "notify me",
]

REFUND_KEYWORDS = [
    "refund",
    "return",
    "money back",
    "cancel order",
    "return policy",
    "can i return",
    "can i refund",
]

PRODUCT_KEYWORDS = [
    "product",
    "in stock",
    "available",
    "price of",
    "how much does",
    "do you sell",
]


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _extract_order_id(message: str) -> int | None:
    """Try to pull an order number out of messages like 'order 42' or 'order #42'."""
    match = re.search(r"order\s*#?\s*(\d+)", message, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def detect_intent(message: str) -> IntentResult:
    """
    Decide what the user wants.

    This is a simple keyword-based version for learning.
    Later we can upgrade it to use OpenAI for smarter detection.
    """
    text = message.lower().strip()
    order_id = _extract_order_id(text)

    if order_id is not None or _contains_any(text, ORDER_KEYWORDS):
        return IntentResult(intent=Intent.ORDER_STATUS, order_id=order_id)

    if _contains_any(text, FAQ_KEYWORDS):
        return IntentResult(intent=Intent.FAQ)

    if _contains_any(text, SHIPPING_POLICY_KEYWORDS):
        return IntentResult(intent=Intent.SHIPPING_POLICY)

    if _contains_any(text, PAYMENT_KEYWORDS):
        return IntentResult(intent=Intent.PAYMENT_POLICY)

    if _contains_any(text, REFUND_KEYWORDS):
        return IntentResult(intent=Intent.REFUND_POLICY)

    if _contains_any(text, PRODUCT_KEYWORDS):
        return IntentResult(intent=Intent.PRODUCT_INFO)

    return IntentResult(intent=Intent.GENERAL)

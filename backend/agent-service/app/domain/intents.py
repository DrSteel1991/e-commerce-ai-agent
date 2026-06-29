from enum import Enum


class Intent(str, Enum):
    """The type of help the user is asking for."""

    ORDER_STATUS = "order_status"
    REFUND_POLICY = "refund_policy"
    SHIPPING_POLICY = "shipping_policy"
    PAYMENT_POLICY = "payment_policy"
    FAQ = "faq"
    PRODUCT_INFO = "product_info"
    GENERAL = "general"

from enum import Enum


class Intent(str, Enum):
    """The type of help the user is asking for."""

    ORDER_STATUS = "order_status"
    REFUND_POLICY = "refund_policy"
    PRODUCT_INFO = "product_info"
    GENERAL = "general"

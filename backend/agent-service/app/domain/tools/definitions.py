"""OpenAI tool schemas the agent can call."""

from openai.types.chat import ChatCompletionToolParam

AGENT_TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "list_products",
            "description": (
                "List products in the store catalog. Use when the customer wants "
                "to browse, see what you sell, or view available items — not when "
                "searching for something specific."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max products to return (default 10).",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter, e.g. Electronics.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Keyword search for products by name, description, or category. "
                "Use when the customer asks about a specific item or type of product."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Short search phrase, e.g. 'wireless headphones'.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 5).",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products_semantic",
            "description": (
                "Semantic / meaning-based product search. Use for vague or natural "
                "descriptions like 'something for running' or 'gift for a coffee lover'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language product description.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 5).",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": (
                "Look up an order's status and total. Requires the customer to be "
                "signed in. Use when they ask about order tracking or delivery status."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The order number, e.g. 42.",
                    },
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Search store policies and FAQs: refunds, returns, shipping, "
                "payment methods, warranties, account help."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The customer's policy or FAQ question.",
                    },
                },
                "required": ["question"],
                "additionalProperties": False,
            },
        },
    },
]

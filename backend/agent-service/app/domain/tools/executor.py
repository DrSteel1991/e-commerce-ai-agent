import json
import logging

from app.services.business_client import (
    get_order_summary,
    list_products,
    search_products,
)
from app.services.rag_client import ask_rag_service, search_products_semantic
from ecommerce_contracts.errors import ServiceError

logger = logging.getLogger(__name__)


async def execute_tool(
    name: str,
    arguments: dict,
    *,
    user_id: str | None,
) -> dict:
    """
    Run a single tool and return a JSON-serializable result for the LLM.
    Never raises — errors are returned in the payload so the model can explain them.
    """
    try:
        if name == "list_products":
            products = await list_products(
                limit=int(arguments.get("limit", 10)),
                category=arguments.get("category"),
            )
            return {"products": products, "count": len(products)}

        if name == "search_products":
            query = str(arguments["query"]).strip()
            limit = int(arguments.get("limit", 5))
            products = await search_products(query, limit=limit)
            return {"products": products, "search_query": query, "count": len(products)}

        if name == "search_products_semantic":
            query = str(arguments["query"]).strip()
            limit = int(arguments.get("limit", 5))
            result = await search_products_semantic(query, limit=limit)
            return result

        if name == "get_order_status":
            if user_id is None:
                return {
                    "error": "auth_required",
                    "message": "Customer must sign in to check order status.",
                }
            order_id = int(arguments["order_id"])
            summary = await get_order_summary(order_id, user_id)
            if summary is None:
                return {
                    "error": "not_found",
                    "message": f"Order #{order_id} was not found.",
                    "order_id": order_id,
                }
            return {"order": summary}

        if name == "search_knowledge_base":
            question = str(arguments["question"]).strip()
            rag = await ask_rag_service(question)
            return {
                "answer": rag.get("answer"),
                "sources": rag.get("sources", []),
            }

        return {"error": "unknown_tool", "message": f"Unknown tool: {name}"}

    except ServiceError as exc:
        return {"error": "service_error", "message": exc.user_message}
    except KeyError as exc:
        return {"error": "invalid_arguments", "message": f"Missing argument: {exc}"}
    except Exception:
        logger.exception("Tool execution failed: %s", name)
        return {
            "error": "internal_error",
            "message": "Something went wrong while fetching that information.",
        }


def serialize_tool_result(result: dict) -> str:
    return json.dumps(result, default=str)

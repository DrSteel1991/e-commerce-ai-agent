import os

import httpx
from dotenv import load_dotenv
from ecommerce_contracts import internal_headers
from ecommerce_contracts.errors import (
    ServiceForbiddenError,
    ServiceUnavailableError,
)

_ = load_dotenv()

BUSINESS_SERVICE_URL = os.environ.get("BUSINESS_SERVICE_URL", "http://localhost:8003")


async def get_order_summary(order_id: int, user_id: str | None) -> dict | None:
    """
    Ask the Business Service for a human-friendly order summary.

    Returns None if the order does not exist.
    Raises ServiceError subclasses for auth, access, and availability issues.
    """
    if user_id is None:
        raise ServiceForbiddenError(
            "Authentication required",
            user_message="Please sign in to check your order status.",
        )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BUSINESS_SERVICE_URL}/orders/{order_id}/summary",
                headers=internal_headers(user_id=user_id),
            )
    except httpx.RequestError as exc:
        raise ServiceUnavailableError(
            "Business service unavailable",
            user_message=(
                "I cannot reach the order system right now. Please try again shortly."
            ),
        ) from exc

    if response.status_code == 404:
        return None

    if response.status_code == 403:
        raise ServiceForbiddenError(
            "Order access denied",
            user_message="You do not have access to that order.",
        )

    if response.status_code == 401:
        raise ServiceForbiddenError(
            "Authentication required",
            user_message="Please sign in to check your order status.",
        )

    if response.status_code >= 500:
        raise ServiceUnavailableError(
            "Business service error",
            user_message=(
                "I cannot reach the order system right now. Please try again shortly."
            ),
        )

    response.raise_for_status()
    return response.json()


async def get_order(order_id: int, user_id: str | None) -> dict | None:
    """Fetch raw order data from the Business Service."""
    if user_id is None:
        raise ServiceForbiddenError(
            "Authentication required",
            user_message="Please sign in to view order details.",
        )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BUSINESS_SERVICE_URL}/orders/{order_id}",
                headers=internal_headers(user_id=user_id),
            )
    except httpx.RequestError as exc:
        raise ServiceUnavailableError(
            "Business service unavailable",
            user_message=(
                "I cannot reach the order system right now. Please try again shortly."
            ),
        ) from exc

    if response.status_code == 404:
        return None

    if response.status_code == 403:
        raise ServiceForbiddenError(
            "Order access denied",
            user_message="You do not have access to that order.",
        )

    if response.status_code >= 500:
        raise ServiceUnavailableError(
            "Business service error",
            user_message=(
                "I cannot reach the order system right now. Please try again shortly."
            ),
        )

    response.raise_for_status()
    return response.json()


async def list_products(
    limit: int = 10, category: str | None = None
) -> list[dict]:
    """List products from the catalog (browse / show all)."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params: dict[str, str | int] = {"limit": limit}
            if category:
                params["category"] = category
            response = await client.get(
                f"{BUSINESS_SERVICE_URL}/products",
                params=params,
                headers=internal_headers(),
            )
    except httpx.RequestError as exc:
        raise ServiceUnavailableError(
            "Business service unavailable",
            user_message=(
                "I cannot load products right now. Please try again shortly."
            ),
        ) from exc

    if response.status_code >= 500:
        raise ServiceUnavailableError(
            "Business service error",
            user_message=(
                "I cannot load products right now. Please try again shortly."
            ),
        )

    response.raise_for_status()
    return response.json()


async def search_products(query: str, limit: int = 5) -> list[dict]:
    """Search products in the Business Service."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BUSINESS_SERVICE_URL}/products/search",
                params={"query": query, "limit": limit},
                headers=internal_headers(),
            )
    except httpx.RequestError as exc:
        raise ServiceUnavailableError(
            "Business service unavailable",
            user_message=(
                "I cannot search products right now. Please try again shortly."
            ),
        ) from exc

    if response.status_code >= 500:
        raise ServiceUnavailableError(
            "Business service error",
            user_message=(
                "I cannot search products right now. Please try again shortly."
            ),
        )

    response.raise_for_status()
    return response.json()

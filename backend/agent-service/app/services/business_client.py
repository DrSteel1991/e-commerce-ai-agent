import os

import httpx
from dotenv import load_dotenv

_ = load_dotenv()

BUSINESS_SERVICE_URL = os.environ.get(
    "BUSINESS_SERVICE_URL", "http://localhost:8003"
)


async def get_order_summary(order_id: int) -> dict | None:
    """
    Ask the Business Service for a human-friendly order summary.

    Returns None if the order does not exist.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BUSINESS_SERVICE_URL}/orders/{order_id}/summary"
        )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


async def get_order(order_id: int) -> dict | None:
    """Fetch raw order data from the Business Service."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BUSINESS_SERVICE_URL}/orders/{order_id}")

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


async def search_products(query: str, limit: int = 5) -> list[dict]:
    """Search products in the Business Service."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BUSINESS_SERVICE_URL}/products/search",
            params={"query": query, "limit": limit},
        )

    response.raise_for_status()
    return response.json()

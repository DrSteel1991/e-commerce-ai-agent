import os

import httpx
from dotenv import load_dotenv
from ecommerce_contracts import internal_headers
from ecommerce_contracts.errors import ServiceUnavailableError

_ = load_dotenv()

RAG_SERVICE_URL = os.environ.get("RAG_SERVICE_URL", "http://localhost:8002")


async def ask_rag_service(question: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{RAG_SERVICE_URL}/rag/ask",
                json={"question": question},
                headers=internal_headers(),
            )
    except httpx.RequestError as exc:
        raise ServiceUnavailableError(
            "RAG service unavailable",
            user_message=(
                "I cannot access our knowledge base right now. Please try again shortly."
            ),
        ) from exc

    if response.status_code >= 500:
        raise ServiceUnavailableError(
            "RAG service error",
            user_message=(
                "I cannot access our knowledge base right now. Please try again shortly."
            ),
        )

    response.raise_for_status()
    return response.json()

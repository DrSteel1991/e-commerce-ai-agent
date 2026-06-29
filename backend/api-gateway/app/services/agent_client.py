import os

import httpx
from dotenv import load_dotenv
from ecommerce_contracts import internal_headers

_ = load_dotenv()

AGENT_SERVICE_URL = os.environ.get("AGENT_SERVICE_URL", "http://localhost:8004")


async def send_message_to_agent(
    message: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    payload = {"message": message, "session_id": session_id}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{AGENT_SERVICE_URL}/agent/chat",
            json=payload,
            headers=internal_headers(user_id=user_id),
        )

    response.raise_for_status()
    return response.json()

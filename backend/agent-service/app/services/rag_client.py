import os

import httpx
from dotenv import load_dotenv

_ = load_dotenv()

RAG_SERVICE_URL = os.environ.get("RAG_SERVICE_URL", "http://localhost:8002")


async def ask_rag_service(question: str) -> dict:
    payload = {"question": question}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{RAG_SERVICE_URL}/rag/ask",
            json=payload,
        )

    response.raise_for_status()
    return response.json()

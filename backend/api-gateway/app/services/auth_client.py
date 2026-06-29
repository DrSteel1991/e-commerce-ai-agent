import os

import httpx
from dotenv import load_dotenv

_ = load_dotenv()

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:8001")


async def login(email: str, password: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/login",
            json={"email": email, "password": password},
        )

    response.raise_for_status()
    return response.json()


async def get_current_user(token: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{AUTH_SERVICE_URL}/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    response.raise_for_status()
    return response.json()

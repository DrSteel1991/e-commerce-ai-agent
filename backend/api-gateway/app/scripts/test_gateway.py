import asyncio
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

GATEWAY_URL = "http://localhost:8000"


async def main():
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("1. Health check")
        response = await client.get(f"{GATEWAY_URL}/health")
        print(response.json())
        print()

        print("2. Chat as guest (policy questions work)")
        response = await client.post(
            f"{GATEWAY_URL}/api/chat",
            json={"message": "What is your refund policy?"},
        )
        print(response.status_code, response.json())
        print()

        print("3. Chat order lookup without login (should ask to sign in)")
        response = await client.post(
            f"{GATEWAY_URL}/api/chat",
            json={"message": "Where is my order #1?"},
        )
        print(response.status_code, response.json())
        print()

        print("4. Login + order lookup with JWT")
        print("   Use a user with a real bcrypt password hash.")
        email = os.environ.get("TEST_USER_EMAIL", "user1@example.com")
        password = os.environ.get("TEST_USER_PASSWORD", "")

        if not password:
            print("   Skipped — set TEST_USER_PASSWORD to run authenticated test.")
            return

        login_response = await client.post(
            f"{GATEWAY_URL}/api/auth/login",
            json={"email": email, "password": password},
        )
        token = login_response.json()["access_token"]

        response = await client.post(
            f"{GATEWAY_URL}/api/chat",
            json={"message": "Where is my order #1?"},
            headers={"Authorization": f"Bearer {token}"},
        )
        print(response.status_code, response.json())


if __name__ == "__main__":
    asyncio.run(main())

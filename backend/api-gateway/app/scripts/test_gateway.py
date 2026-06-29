"""
Quick manual test for the API Gateway.

Usage:
  1. Start Auth Service on port 8001
  2. Start Agent Service on port 8004
  3. Start Business + RAG if testing chat with orders/refunds
  4. Start API Gateway on port 8000
  5. Run: python -m app.scripts.test_gateway
"""

import asyncio

import httpx

GATEWAY_URL = "http://localhost:8000"


async def main():
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("1. Health check")
        response = await client.get(f"{GATEWAY_URL}/health")
        print(response.json())
        print()

        print("2. Chat (no login required for now)")
        response = await client.post(
            f"{GATEWAY_URL}/api/chat",
            json={
                "message": "Where is my order #1?",
                "user_id": "demo-user",
            },
        )
        print(response.status_code, response.json())
        print()

        print("3. Login")
        print("   Use a real user from your database, e.g. user1@example.com")
        print("   Skip this step if you have not set a real password hash yet.")


if __name__ == "__main__":
    asyncio.run(main())

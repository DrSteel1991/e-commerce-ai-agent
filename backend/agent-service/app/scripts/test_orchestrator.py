import asyncio

from app.domain.services.agent_orchestrator import handle_message


async def main():
    test_messages = [
        "Where is my order #1?",
        "Can I get a refund?",
        "Do you have shoes in stock?",
        "Where is my order?",
        "Hello",
    ]

    print("Agent orchestrator test\n")
    print("Requires OPENAI_API_KEY in backend/agent-service/.env")
    print("Make sure these services are running:")
    print("  Business Service → port 8003")
    print("  RAG Service      → port 8002\n")

    for message in test_messages:
        result = await handle_message(
            message,
            user_id="00000000-0000-4000-8000-000000000001",
        )

        print(f"Message: {message}")
        print(f"  Intent:  {result['intent']}")
        print(f"  Action:  {result['agent_action']}")
        print(f"  Answer:  {result['answer'][:120]}...")
        print()


if __name__ == "__main__":
    asyncio.run(main())

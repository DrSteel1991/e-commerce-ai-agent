import asyncio

from app.domain.services.intent_service import detect_intent_keywords
from app.domain.services.llm_intent_service import detect_intent


async def main():
    test_messages = [
        "Where is my order #42?",
        "Can I get a refund?",
        "Do you have running shoes in stock?",
        "Hello, I need help",
        "What is the status of order 15?",
        "Can I return this item after 7 days?",
    ]

    print("Keyword fallback intent detection\n")

    for message in test_messages:
        result = detect_intent_keywords(message)
        print(f"Message: {message}")
        print(f"  Intent:       {result.intent.value}")
        print(f"  Order ID:     {result.order_id}")
        print(f"  Search query: {result.search_query}")
        print()

    print("LLM intent detection (requires OPENAI_API_KEY)\n")

    history = [
        {"role": "user", "content": "Where is my order #12?"},
        {
            "role": "assistant",
            "content": "Order #12 is shipped and should arrive soon.",
        },
    ]

    follow_up = "Can I return it if it does not fit?"
    result = await detect_intent(follow_up, history)
    print(f"Message: {follow_up}")
    print(f"  Intent:       {result.intent.value}")
    print(f"  Order ID:     {result.order_id}")
    print(f"  Search query: {result.search_query}")


if __name__ == "__main__":
    asyncio.run(main())

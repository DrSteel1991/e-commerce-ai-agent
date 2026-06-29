from app.domain.services.intent_service import detect_intent


def main():
    test_messages = [
        "Where is my order #42?",
        "Can I get a refund?",
        "Do you have running shoes in stock?",
        "Hello, I need help",
        "What is the status of order 15?",
        "Can I return this item after 7 days?",
    ]

    print("Intent detection test\n")

    for message in test_messages:
        result = detect_intent(message)
        print(f"Message: {message}")
        print(f"  Intent:   {result.intent.value}")
        print(f"  Order ID: {result.order_id}")
        print()


if __name__ == "__main__":
    main()

import asyncio

from app.services.business_client import get_order, get_order_summary


async def main():
    test_order_ids = [1, 99999]

    print("Business Service client test\n")
    print("Make sure Business Service is running:")
    print("  cd backend/business-service")
    print("  uvicorn app.main:app --reload --port 8003\n")

    for order_id in test_order_ids:
        print(f"--- Order {order_id} ---")

        summary = await get_order_summary(order_id)

        if summary is None:
            print("  Summary: not found")
        else:
            print(f"  Status:  {summary['status']}")
            print(f"  Message: {summary['message']}")

        order = await get_order(order_id)

        if order is None:
            print("  Raw order: not found")
        else:
            print(f"  Raw order: id={order['id']}, status={order['status']}")

        print()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from app.services.business_client import get_order, get_order_summary

# Deterministic user1 ID from database/auth_db/seed.sql
USER1_ID = "00000000-0000-4000-8000-000000000001"


async def main():
    test_order_ids = [1, 99999]

    print("Business Service client test\n")
    print("Make sure Business Service is running:")
    print("  cd backend/business-service")
    print("  uvicorn app.main:app --reload --port 8003\n")

    for order_id in test_order_ids:
        print(f"--- Order {order_id} ---")

        summary = await get_order_summary(order_id, USER1_ID)

        if summary is None:
            print("  Summary: not found")
        else:
            print(f"  Status:  {summary['status']}")
            print(f"  Message: {summary['message']}")

        order = await get_order(order_id, USER1_ID)

        if order is None:
            print("  Raw order: not found")
        else:
            print(f"  Raw order: id={order['id']}, status={order['status']}")

        print()


if __name__ == "__main__":
    asyncio.run(main())

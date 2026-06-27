from app.domain.services.retrieval_service import retrieve_context
from app.infrastructure.database.database import SessionLocal


def main():
    db = SessionLocal()

    try:
        question = "Can I return my shoes after 7 days?"

        print("=" * 80)
        print(f"Question: {question}")
        print("=" * 80)

        chunks = retrieve_context(db=db, question=question, limit=3)

        for index, chunk in enumerate(chunks, start=1):
            print(f"\nResult {index}")
            print("-" * 80)
            print(f"Distance : {chunk.distance:.4f}")
            print(chunk.content)
            print()

    finally:
        db.close()


if __name__ == "__main__":
    main()

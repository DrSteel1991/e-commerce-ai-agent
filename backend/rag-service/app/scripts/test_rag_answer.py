from app.domain.services.rag_service import answer_question
from app.infrastructure.database.database import SessionLocal


def main():
    db = SessionLocal()

    try:
        result = answer_question(
            db=db, question="Can I return my shoes after 7 days?", limit=3
        )

        print("QUESTION:")
        print(result["question"])

        print("\nANSWER:")
        print(result["answer"])

        print("\nSOURCES:")
        for source in result["sources"]:
            print(f"Chunk ID: {source['chunk_id']}")
            print(f"Distance: {source['distance']}")
            print(f"Preview: {source['preview']}")
            print("-" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    main()

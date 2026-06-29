from pathlib import Path

from app.domain.services.ingestion_service import ingest_pdf
from app.infrastructure.database.database import SessionLocal


def main():
    project_root = Path(__file__).resolve().parents[3]

    pdf_path = project_root / "documents" / "refund_policy.pdf"

    db = SessionLocal()

    try:
        result = ingest_pdf(
            db=db,
            file_path=str(pdf_path),
            filename="refund_policy.pdf",
            document_type="policy",
            replace=True,
        )

        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()

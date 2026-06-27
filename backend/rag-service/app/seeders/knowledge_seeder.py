from pathlib import Path

from app.domain.services.ingestion_service import ingest_pdf
from app.infrastructure.database.database import SessionLocal


def main():
    project_root = Path(__file__).resolve().parents[3]
    documents_dir = project_root / "documents"

    pdf_files = list(documents_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found.")
        return

    db = SessionLocal()

    try:
        for pdf_path in pdf_files:
            print(f"Ingesting {pdf_path.name}...")

            result = ingest_pdf(
                db=db,
                file_path=str(pdf_path),
                filename=pdf_path.name,
                document_type="policy",
            )

            print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()

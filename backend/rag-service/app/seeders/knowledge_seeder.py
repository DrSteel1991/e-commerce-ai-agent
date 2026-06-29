"""
Ingest every PDF in backend/documents/ into the RAG database.

Run after generating PDFs:

    cd backend/rag-service
    source .venv/bin/activate
    python -m app.scripts.generate_policy_pdfs   # optional, creates PDFs from content/*.txt
    python -m app.seeders.knowledge_seeder      # chunk + embed + store vectors
"""

from pathlib import Path

from app.domain.services.ingestion_service import ingest_pdf
from app.infrastructure.database.database import SessionLocal

DOCUMENT_TYPES = {
    "refund_policy.pdf": "policy",
    "shipping_policy.pdf": "policy",
    "payment_policy.pdf": "policy",
    "warranty_policy.pdf": "policy",
    "faq.pdf": "faq",
}


def document_type_for(filename: str) -> str:
    return DOCUMENT_TYPES.get(filename, "policy")


def main():
    project_root = Path(__file__).resolve().parents[3]
    documents_dir = project_root / "documents"

    pdf_files = sorted(documents_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in backend/documents/")
        return

    db = SessionLocal()

    try:
        total_chunks = 0

        for pdf_path in pdf_files:
            doc_type = document_type_for(pdf_path.name)
            print(f"Ingesting {pdf_path.name} ({doc_type})...")

            result = ingest_pdf(
                db=db,
                file_path=str(pdf_path),
                filename=pdf_path.name,
                document_type=doc_type,
                replace=True,
            )

            print(f"  -> {result['status']}, {result['chunks_created']} chunks")
            total_chunks += result["chunks_created"]

        print(f"\nDone. {len(pdf_files)} documents, {total_chunks} chunks created.")

    finally:
        db.close()


if __name__ == "__main__":
    main()

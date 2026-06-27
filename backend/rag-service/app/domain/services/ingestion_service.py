from app.domain.repositories.document_repository import (
    create_document,
    create_document_chunk,
    get_document_by_filename,
)
from app.domain.services.chunking_service import chunk_text
from app.infrastructure.embeddings.openai_embedding_client import create_embedding
from app.infrastructure.pdf_loader import extract_text_from_pdf
from sqlalchemy.orm import Session


def ingest_pdf(
    db: Session, file_path: str, filename: str, document_type: str | None = "policy"
):
    existing_document = get_document_by_filename(db=db, filename=filename)

    if existing_document:
        return {
            "document_id": existing_document.id,
            "filename": existing_document.filename,
            "chunks_created": 0,
            "status": "skipped_already_ingested",
        }

    text = extract_text_from_pdf(file_path)

    chunks = chunk_text(text=text, chunk_size=500, overlap=100)

    document = create_document(db=db, filename=filename, document_type=document_type)

    for index, chunk in enumerate(chunks):
        embedding = create_embedding(chunk)

        create_document_chunk(
            db=db,
            document_id=document.id,
            content=chunk,
            embedding=embedding,
            chunk_index=index,
        )

    return {
        "document_id": document.id,
        "filename": document.filename,
        "chunks_created": len(chunks),
    }

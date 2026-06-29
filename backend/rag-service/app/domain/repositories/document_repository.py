from app.infrastructure.database.models.document_chunk_model import DocumentChunk
from app.infrastructure.database.models.document_model import Document
from sqlalchemy.orm import Session


def create_document(db: Session, filename: str, document_type: str | None = None):
    document = Document(filename=filename, document_type=document_type)

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def create_document_chunk(
    db: Session,
    document_id: int,
    content: str,
    embedding: list[float],
    chunk_index: int,
):
    chunk = DocumentChunk(
        document_id=document_id,
        content=content,
        embedding=embedding,
        chunk_index=chunk_index,
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk


def get_document_by_filename(db: Session, filename: str):
    return db.query(Document).filter(Document.filename == filename).first()


def delete_document_by_filename(db: Session, filename: str) -> bool:
    document = get_document_by_filename(db, filename)
    if not document:
        return False

    db.delete(document)
    db.commit()
    return True

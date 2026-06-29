from app.infrastructure.database.models.document_chunk_model import DocumentChunk
from app.infrastructure.database.models.document_model import Document
from sqlalchemy.orm import Session


def retrieve_similar_chunks(
    db: Session,
    embedding: list[float],
    limit: int = 5,
    document_type: str | None = None,
):
    query = (
        db.query(
            DocumentChunk.id.label("id"),
            Document.filename.label("filename"),
            Document.document_type.label("document_type"),
            DocumentChunk.content.label("content"),
            DocumentChunk.embedding.cosine_distance(embedding).label("distance"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
    )

    if document_type:
        query = query.filter(Document.document_type == document_type)

    return (
        query.order_by(DocumentChunk.embedding.cosine_distance(embedding))
        .limit(limit)
        .all()
    )

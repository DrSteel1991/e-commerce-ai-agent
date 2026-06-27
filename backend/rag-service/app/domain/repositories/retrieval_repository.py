from app.infrastructure.database.models.document_chunk_model import DocumentChunk
from app.infrastructure.database.models.document_model import Document
from sqlalchemy.orm import Session


def retrieve_similar_chunks(db: Session, embedding: list[float], limit: int = 5):
    results = (
        db.query(
            DocumentChunk.id.label("id"),
            Document.filename.label("filename"),
            DocumentChunk.content.label("content"),
            DocumentChunk.embedding.cosine_distance(embedding).label("distance"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .order_by(DocumentChunk.embedding.cosine_distance(embedding))
        .limit(limit)
        .all()
    )

    return results

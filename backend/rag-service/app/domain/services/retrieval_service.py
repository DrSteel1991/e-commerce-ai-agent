from app.domain.repositories.retrieval_repository import retrieve_similar_chunks
from app.infrastructure.embeddings.openai_embedding_client import create_embedding
from sqlalchemy.orm import Session


def retrieve_context(
    db: Session, question: str, limit: int = 5, document_type: str | None = None
):
    """
    Converts a user question into an embedding,
    retrieves the closest chunks,
    and returns them.
    """

    question_embedding = create_embedding(question)

    chunks = retrieve_similar_chunks(
        db=db,
        embedding=question_embedding,
        limit=limit,
        document_type=document_type,
    )

    return chunks

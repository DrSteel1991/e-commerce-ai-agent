from app.domain.repositories.retrieval_repository import retrieve_similar_chunks
from app.infrastructure.embeddings.openai_embedding_client import create_embedding
from sqlalchemy.orm import Session


def retrieve_context(db: Session, question: str, limit: int = 5):
    """
    Converts a user question into an embedding,
    retrieves the closest chunks,
    and returns them.
    """

    question_embedding = create_embedding(question)

    chunks = retrieve_similar_chunks(db=db, embedding=question_embedding, limit=limit)

    return chunks

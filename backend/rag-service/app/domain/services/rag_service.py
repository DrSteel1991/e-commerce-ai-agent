from app.domain.services.prompt_builder import build_rag_prompt
from app.domain.services.retrieval_service import retrieve_context
from app.infrastructure.llm.openai_llm_client import generate_answer
from sqlalchemy.orm import Session


def answer_question(db: Session, question: str, limit: int = 5):
    chunks = retrieve_context(db=db, question=question, limit=limit)

    prompt = build_rag_prompt(question=question, context_chunks=chunks)

    answer = generate_answer(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": [
            {
                "chunk_id": chunk.id,
                "filename": chunk.filename,
                "distance": float(chunk.distance),
                "preview": chunk.content,
            }
            for chunk in chunks
        ],
    }

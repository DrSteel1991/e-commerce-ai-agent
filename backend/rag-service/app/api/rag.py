from app.domain.services.rag_service import answer_question
from app.infrastructure.database.database import get_db
from ecommerce_contracts import AskRequest, AskResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    return answer_question(db=db, question=request.question, limit=5)

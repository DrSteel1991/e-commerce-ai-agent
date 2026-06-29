from app.domain.services.product_search_service import search_products
from app.domain.services.rag_service import answer_question
from app.infrastructure.database.database import get_db
from ecommerce_contracts import AskRequest, AskResponse, ProductSearchRequest, ProductSearchResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    return answer_question(db=db, question=request.question, limit=5)


@router.post("/search-products", response_model=ProductSearchResponse)
def search_products_endpoint(
    request: ProductSearchRequest, db: Session = Depends(get_db)
):
    return search_products(db=db, query=request.query, limit=request.limit)

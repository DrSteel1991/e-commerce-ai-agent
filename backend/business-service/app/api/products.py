from app.domain.services.product_service import (
    list_low_stock_products,
    list_products_by_category,
    search_available_products,
)
from app.infrastructure.database.database import get_db
from app.schemas.product_schemas import ProductResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/low-stock", response_model=list[ProductResponse])
def get_low_stock(limit: int = 20, db: Session = Depends(get_db)):
    return list_low_stock_products(db, limit)


@router.get("/search", response_model=list[ProductResponse])
def search_products(query: str, limit: int = 20, db: Session = Depends(get_db)):
    return search_available_products(db, query, limit)


@router.get("/category/{category}", response_model=list[ProductResponse])
def get_by_category(category: str, limit: int = 20, db: Session = Depends(get_db)):
    return list_products_by_category(db, category, limit)

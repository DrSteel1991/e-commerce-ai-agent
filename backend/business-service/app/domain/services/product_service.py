from app.domain.repositories.product_repository import (
    get_low_stock_products,
    get_products_by_category,
    search_products,
)
from sqlalchemy.orm import Session


def list_low_stock_products(db: Session, limit: int = 20):
    return get_low_stock_products(db, limit)


def search_available_products(db: Session, query: str, limit: int = 20):
    return search_products(db, query, limit)


def list_products_by_category(db: Session, category: str, limit: int = 20):
    return get_products_by_category(db, category, limit)

import re

from app.infrastructure.database.models.product_model import Product
from sqlalchemy import case, or_
from sqlalchemy.orm import Session

_STOP_WORDS = frozenset(
    {"how", "much", "does", "it", "cost", "the", "a", "an", "is", "for", "of", "what"}
)


def list_products(db: Session, limit: int = 20, category: str | None = None):
    query = db.query(Product).order_by(Product.name.asc())

    if category:
        query = query.filter(Product.category.ilike(category))

    return query.limit(limit).all()


def get_low_stock_products(db: Session, limit: int = 20):
    return (
        db.query(Product)
        .filter(Product.stock <= 10)
        .order_by(Product.stock.asc())
        .limit(limit)
        .all()
    )


def _order_by_relevance(query: str):
    normalized = query.strip()
    return (
        case((Product.name.ilike(normalized), 0), else_=1),
        Product.name.asc(),
    )


def search_products(db: Session, query: str, limit: int = 20):
    pattern = f"%{query}%"
    results = (
        db.query(Product)
        .filter(
            or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
                Product.category.ilike(pattern),
            )
        )
        .order_by(*_order_by_relevance(query))
        .limit(limit)
        .all()
    )
    if results:
        return results

    tokens = [
        token
        for token in re.split(r"\W+", query)
        if len(token) > 1 and token.lower() not in _STOP_WORDS
    ]
    if len(tokens) < 2:
        return results

    token_query = db.query(Product)
    for token in tokens:
        token_pattern = f"%{token}%"
        token_query = token_query.filter(
            or_(
                Product.name.ilike(token_pattern),
                Product.description.ilike(token_pattern),
                Product.category.ilike(token_pattern),
            )
        )

    return token_query.order_by(*_order_by_relevance(query)).limit(limit).all()


def get_products_by_category(db: Session, category: str, limit: int = 20):
    return db.query(Product).filter(Product.category == category).limit(limit).all()

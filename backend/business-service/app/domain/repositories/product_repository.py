from app.infrastructure.database.models.product_model import Product
from sqlalchemy.orm import Session


def get_low_stock_products(db: Session, limit: int = 20):
    return (
        db.query(Product)
        .filter(Product.stock <= 10)
        .order_by(Product.stock.asc())
        .limit(limit)
        .all()
    )


def search_products(db: Session, query: str, limit: int = 20):
    return db.query(Product).filter(Product.name.ilike(f"%{query}%")).limit(limit).all()


def get_products_by_category(db: Session, category: str, limit: int = 20):
    return db.query(Product).filter(Product.category == category).limit(limit).all()

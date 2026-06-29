"""
Sync products from business_db into rag_db as embedded catalog chunks.

Run from backend/rag-service (requires BUSINESS_DATABASE_URL or reads business .env):

    python -m app.seeders.product_catalog_seeder
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from app.domain.services.ingestion_service import ingest_text_document
from app.infrastructure.database.database import SessionLocal

PRODUCT_CATALOG_FILENAME = "product_catalog.txt"
DOCUMENT_TYPE = "product_catalog"


def _business_database_url() -> str:
    load_dotenv()
    url = os.environ.get("BUSINESS_DATABASE_URL")
    if url:
        return url

    business_env = Path(__file__).resolve().parents[3] / "business-service" / ".env"
    if business_env.exists():
        for line in business_env.read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip()

    raise RuntimeError(
        "Set BUSINESS_DATABASE_URL or ensure backend/business-service/.env has DATABASE_URL"
    )


def _format_product_row(row: dict) -> str:
    return (
        f"Product ID: {row['id']}\n"
        f"Name: {row['name']}\n"
        f"Category: {row.get('category') or 'General'}\n"
        f"Price: ${row['price']}\n"
        f"Stock: {row['stock']} in stock\n"
        f"Description: {row.get('description') or 'No description available.'}"
    )


def fetch_products() -> list[dict]:
    engine = create_engine(_business_database_url())
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, name, description, price, stock, category
                FROM products
                ORDER BY id
                """
            )
        ).mappings().all()

    return [dict(row) for row in rows]


def main():
    products = fetch_products()

    if not products:
        print("No products found in business_db.")
        return

    catalog_text = "\n\n---\n\n".join(_format_product_row(p) for p in products)

    db = SessionLocal()
    try:
        result = ingest_text_document(
            db=db,
            filename=PRODUCT_CATALOG_FILENAME,
            text=catalog_text,
            document_type=DOCUMENT_TYPE,
            replace=True,
        )
        print(
            f"Product catalog ingested: {result['status']}, "
            f"{result['chunks_created']} chunks from {len(products)} products."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()

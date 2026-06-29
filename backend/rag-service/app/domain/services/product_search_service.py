import re

from app.domain.services.retrieval_service import retrieve_context
from sqlalchemy.orm import Session

PRODUCT_ID_PATTERN = re.compile(r"Product ID:\s*(\d+)", re.IGNORECASE)


def _parse_product_from_chunk(content: str) -> dict:
    """Extract structured fields from an ingested product catalog chunk."""
    fields: dict[str, str] = {}
    for line in content.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip().lower()] = value.strip()

    product_id = None
    match = PRODUCT_ID_PATTERN.search(content)
    if match:
        product_id = int(match.group(1))
    elif "product id" in fields:
        try:
            product_id = int(fields["product id"])
        except ValueError:
            product_id = None

    price_raw = fields.get("price", "")
    price = price_raw.lstrip("$") if price_raw else None

    stock_raw = fields.get("stock", "")
    stock = None
    if stock_raw:
        try:
            stock = int(stock_raw.split()[0])
        except ValueError:
            stock = None

    return {
        "id": product_id,
        "name": fields.get("name"),
        "category": fields.get("category"),
        "price": price,
        "stock": stock,
        "description": fields.get("description"),
        "preview": content[:300],
    }


def search_products(db: Session, query: str, limit: int = 5) -> dict:
    chunks = retrieve_context(
        db=db,
        question=query,
        limit=limit,
        document_type="product_catalog",
    )

    products = [_parse_product_from_chunk(chunk.content) for chunk in chunks]

    return {
        "query": query,
        "products": products,
        "count": len(products),
        "sources": [
            {
                "chunk_id": chunk.id,
                "filename": chunk.filename,
                "distance": float(chunk.distance),
                "preview": chunk.content[:200],
            }
            for chunk in chunks
        ],
    }

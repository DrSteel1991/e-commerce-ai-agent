from app.api.orders import router as orders_router
from app.api.products import router as products_router
from app.infrastructure.database.database import engine
from ecommerce_contracts import require_internal_api_key
from fastapi import Depends, FastAPI
from sqlalchemy import text

app = FastAPI(title="Business Service")

app.include_router(
    products_router,
    dependencies=[Depends(require_internal_api_key)],
)
app.include_router(
    orders_router,
    dependencies=[Depends(require_internal_api_key)],
)


@app.get("/health")
def health_check():
    return {"status": "business-service running"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database();"))
        database_name = result.scalar()

    return {"status": "connected", "database": database_name}

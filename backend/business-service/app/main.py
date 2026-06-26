from app.api.orders import router as orders_router
from app.api.products import router as products_router
from app.infrastructure.database.database import engine
from fastapi import FastAPI
from sqlalchemy import text

app = FastAPI(title="Business Service")

app.include_router(products_router)
app.include_router(orders_router)


@app.get("/health")
def health_check():
    return {"status": "business-service running"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database();"))
        database_name = result.scalar()

    return {"status": "connected", "database": database_name}

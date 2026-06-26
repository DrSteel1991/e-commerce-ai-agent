from fastapi import FastAPI
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.infrastructure.database.database import engine

app = FastAPI(title="Auth Service")

app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {"status": "auth-service running"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database();"))
        database_name = result.scalar()

    return {"status": "connected", "database": database_name}

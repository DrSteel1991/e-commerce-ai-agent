from app.api.rag import router as rag_router
from app.infrastructure.database.database import engine
from fastapi import FastAPI
from sqlalchemy import text

app = FastAPI(title="RAG Service")

app.include_router(rag_router)


@app.get("/health")
def health_check():
    return {"status": "rag-service running"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        database_name = conn.execute(text("SELECT current_database();")).scalar()

    return {"status": "connected", "database": database_name}

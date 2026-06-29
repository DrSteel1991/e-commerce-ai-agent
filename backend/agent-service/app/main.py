from app.routers.agent_router import router as agent_router
from fastapi import FastAPI

app = FastAPI(
    title="AI E-Commerce Agent Service",
    version="1.0.0",
)

app.include_router(agent_router, prefix="/agent", tags=["Agent"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "agent-service"}

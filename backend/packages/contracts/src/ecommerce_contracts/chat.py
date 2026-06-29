from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Client sends only the message. user_id comes from a verified JWT at the gateway."""

    message: str = Field(min_length=1)


class ChatSource(BaseModel):
    chunk_id: int
    filename: str
    distance: float
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = []
    agent_action: str | None = None
    intent: str | None = None
    user_id: str | None = None
    data: dict | None = None

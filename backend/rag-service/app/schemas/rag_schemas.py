from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class SourceResponse(BaseModel):
    chunk_id: int
    filename: str
    distance: float
    preview: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]

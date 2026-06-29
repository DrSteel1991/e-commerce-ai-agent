from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class SourceResponse(BaseModel):
    chunk_id: int
    filename: str
    distance: float
    preview: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]

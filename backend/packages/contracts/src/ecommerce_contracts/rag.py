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


class ProductSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class ProductSearchHit(BaseModel):
    id: int | None = None
    name: str | None = None
    category: str | None = None
    price: str | None = None
    stock: int | None = None
    description: str | None = None
    preview: str | None = None


class ProductSearchResponse(BaseModel):
    query: str
    products: list[ProductSearchHit]
    count: int
    sources: list[SourceResponse] = []

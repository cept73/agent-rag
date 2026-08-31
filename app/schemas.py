from pydantic import BaseModel, Field


class MaterialCreate(BaseModel):
    slot: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)


class SearchRequest(BaseModel):
    slot: str = Field(min_length=1, max_length=200)
    params: list[str] = Field(min_length=1)

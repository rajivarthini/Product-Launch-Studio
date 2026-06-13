from pydantic import BaseModel, Field


class Listing(BaseModel):
    title: str = ""
    description: str = ""
    bullet_points: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


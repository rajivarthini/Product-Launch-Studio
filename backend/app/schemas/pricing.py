from pydantic import BaseModel, Field


class PriceRange(BaseModel):
    min: float = 0.0
    max: float = 0.0


class Competitor(BaseModel):
    title: str = ""
    price: float = 0.0
    source: str = ""
    url: str = ""


class PricingInfo(BaseModel):
    currency: str = "INR"
    estimated_price_range: PriceRange = Field(default_factory=PriceRange)
    example_competitors: list[Competitor] = Field(default_factory=list)


from pydantic import BaseModel, Field

from .platform_rules import PlatformEnum


class ProductCategory(BaseModel):
    platform_category: str = ""
    platform_subcategory: str = ""


class ProductAttributes(BaseModel):
    color: str = ""
    material: str = ""
    visible_features: list[str] = Field(default_factory=list)


class ProductAnalysis(BaseModel):
    identified_product: str = ""
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    category: ProductCategory = Field(default_factory=ProductCategory)
    attributes: ProductAttributes = Field(default_factory=ProductAttributes)
    platform: PlatformEnum | None = None


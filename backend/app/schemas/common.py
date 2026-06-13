from pydantic import BaseModel, Field


class DimensionInput(BaseModel):
    height: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    dimension_unit: str = Field("cm", min_length=1, max_length=10)
    weight_unit: str = Field("g", min_length=1, max_length=10)


class ImageUrls(BaseModel):
    original_product_image_url: str
    cleaned_product_image_url: str | None = None
    packaging_mockup_image_url: str | None = None


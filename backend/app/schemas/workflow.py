from pydantic import BaseModel, Field
from typing import Optional
from .product import ProductAnalysis
from .license import LicenseAnalysis
from .listing import Listing
from .packaging import PackagingInfo
from .platform_rules import PlatformInfo
from .pricing import PricingInfo


class WorkflowInputs(BaseModel):
    height: float
    width: float
    weight: float
    dimension_unit: str = "cm"
    weight_unit: str = "g"
    description: str


class ImagesResponse(BaseModel):
    original_images: list[str] = Field(default_factory=list)
    cleaned_images: list[str] = Field(default_factory=list)

class WorkflowResponse(BaseModel):
    success: bool = True
    platform: PlatformInfo
    inputs: WorkflowInputs
    product_analysis: ProductAnalysis
    license_analysis: LicenseAnalysis
    listing: Listing
    images: ImagesResponse
    packaging: PackagingInfo
    pricing: PricingInfo | None = None
    disclaimers: list[str] = Field(default_factory=list)


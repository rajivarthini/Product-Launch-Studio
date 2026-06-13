from pydantic import BaseModel, Field


class PackagingDimensions(BaseModel):
    height: float = Field(0, ge=0)
    width: float = Field(0, ge=0)
    weight_support_note: str = ""
    unit: str = "cm"


class PackagingInfo(BaseModel):
    recommended_packaging_type: str = ""
    packaging_material: str = ""
    packaging_dimensions: PackagingDimensions = Field(
        default_factory=PackagingDimensions
    )
    dieline_template_status: str = ""
    design_notes: list[str] = Field(default_factory=list)
    packaging_mockup_image_url: str = ""
    dieline_payload: dict | None = None
    dieline_download_url: str | None = None


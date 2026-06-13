from pydantic import BaseModel, Field


class LicenseAnalysis(BaseModel):
    document_type: str = ""
    extracted_text: str = ""
    license_numbers: list[str] = Field(default_factory=list)
    issuing_authority: str = ""
    product_match_assessment: str = ""
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "Compliance guidance only. Manual verification required."
    )


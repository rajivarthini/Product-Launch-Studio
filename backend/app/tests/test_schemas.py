from app.schemas.workflow import WorkflowResponse
from app.schemas.platform_rules import PlatformEnum, PlatformInfo, PlatformRulesSummary
from app.schemas.product import ProductAnalysis
from app.schemas.license import LicenseAnalysis
from app.schemas.listing import Listing
from app.schemas.packaging import PackagingInfo, PackagingDimensions


def test_workflow_response_shape_minimal():
    platform_rules = PlatformRulesSummary(
        image_rules=[],
        listing_rules=[],
        compliance_notes=[],
        disclaimer="test",
    )
    platform = PlatformInfo(selected=PlatformEnum.amazon, rules_summary=platform_rules)

    product_analysis = ProductAnalysis()
    license_analysis = LicenseAnalysis()
    listing = Listing()
    packaging = PackagingInfo(packaging_dimensions=PackagingDimensions())

    resp = WorkflowResponse(
        success=True,
        platform=platform,
        inputs={
            "height": 10.0,
            "width": 5.0,
            "weight": 100.0,
            "dimension_unit": "cm",
            "weight_unit": "g",
            "description": "Test product",
        },
        product_analysis=product_analysis,
        license_analysis=license_analysis,
        listing=listing,
        images={
            "original_images": ["http://example.com/original.jpg"],
            "cleaned_images": ["http://example.com/cleaned.jpg"],
        },
        packaging=packaging,
        disclaimers=["a", "b"],
    )

    assert resp.success is True
    assert resp.platform.selected == PlatformEnum.amazon
    assert isinstance(resp.product_analysis, ProductAnalysis)
    assert isinstance(resp.license_analysis, LicenseAnalysis)
    assert isinstance(resp.listing, Listing)
    assert isinstance(resp.packaging, PackagingInfo)


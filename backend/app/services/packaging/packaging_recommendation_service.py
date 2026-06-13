
from typing import TYPE_CHECKING
from app.schemas.packaging import PackagingInfo, PackagingDimensions
from app.core.logging import get_logger

if TYPE_CHECKING:
    import app.schemas.product

logger = get_logger(__name__)


class PackagingRecommendationService:
    def recommend(
        self,
        height: float,
        width: float,
        weight: float,
        dimension_unit: str,
        weight_unit: str,
        product_analysis: "app.schemas.product.ProductAnalysis | None" = None,
    ) -> PackagingInfo:
        """
        Suggests a packaging template from templatemaker.nl based on product dimensions.
        """
        # Margin for fitting
        margin_factor = 1.15
        rec_height = round(height * margin_factor, 1)
        rec_width = round(width * margin_factor, 1)
        
        # We'll use Depth as a 3rd dimension derived from height/width ratio or analysis if available
        # But since we only have height/width/weight from inputs, we'll assume a boxy shape or use width as depth for now
        # Ideally, ProductAnalysis would give us 3D dims.
        rec_depth = round(min(rec_height, rec_width) * 0.8, 1)

        # 1. Analyze Type from Templatemaker
        # Types: giftbox, matchbox, mailer, pillowpack, boxwithlid
        suggested_template = "giftbox" # default
        
        prod_name = (product_analysis.identified_product or "").lower() if product_analysis else ""
        mat_hint = (product_analysis.attributes.material or "").lower() if product_analysis and product_analysis.attributes else ""

        if any(x in prod_name for x in ["watch", "jewelry", "premium", "gift"]):
            suggested_template = "boxwithlid"
        elif any(x in prod_name for x in ["card", "wallet", "flat"]):
            suggested_template = "matchbox"
        elif any(x in prod_name for x in ["shirt", "clothing", "fabric"]):
            suggested_template = "pillowpack"
        elif weight > 1000: # Over 1kg
            suggested_template = "mailer"

        # 2. Suggest Material
        # Based on weight
        if weight < 100:
            suggested_material = "Cardstock (250gsm)"
        elif weight < 500:
            suggested_material = "Heavy Cardboard (350gsm)"
        elif weight < 2000:
            suggested_material = "E-Flute Corrugated Cardboard"
        else:
            suggested_material = "B-Flute Corrugated Cardboard (Heavy Duty)"

        design_notes = [
            f"Template suggested: {suggested_template} from templatemaker.nl",
            "Ensure the template is scaled to accommodate the product width and height.",
        ]

        if "fragile" in prod_name or "glass" in mat_hint:
             design_notes.append("Fragile item: Add internal foam or bubble wrap inserts.")

        dimensions = PackagingDimensions(
            height=rec_height,
            width=rec_width,
            weight_support_note=(
                f"Material {suggested_material} selected to support {weight}{weight_unit}."
            ),
            unit=dimension_unit,
        )

        return PackagingInfo(
            recommended_packaging_type=suggested_template,
            packaging_material=suggested_material,
            packaging_dimensions=dimensions,
            dieline_template_status=f"SUGGESTED_TEMPLATE_{suggested_template.upper()}",
            design_notes=design_notes,
            packaging_mockup_image_url=f"https://www.templatemaker.nl/assets/images/{suggested_template}.png",
            dieline_payload=None,
            dieline_download_url=None,
        )

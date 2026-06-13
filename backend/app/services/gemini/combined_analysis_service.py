from typing import Any, Dict, Optional

from app.core.logging import get_logger
from app.schemas.listing import Listing
from app.schemas.license import LicenseAnalysis
from app.schemas.platform_rules import PlatformEnum
from app.schemas.product import ProductAnalysis
from app.services.gemini.client import GeminiClient
from app.services.gemini.prompt_builder import build_combined_analysis_prompt

logger = get_logger(__name__)


class CombinedAnalysisService:
    """
    Performs product analysis, license analysis, and listing generation
    in a SINGLE Gemini API call to avoid rate limit exhaustion.
    """

    def __init__(self, client: GeminiClient | None = None) -> None:
        self.client = client or GeminiClient()

    async def analyze(
        self,
        description: str,
        platform: PlatformEnum,
        height: float,
        width: float,
        weight: float,
        dimension_unit: str,
        weight_unit: str,
        product_name_hint: str | None,
        product_material_hint: str | None,
        product_image_paths: list[str] | None = None,
        license_image_path: str | None = None,
    ) -> tuple[ProductAnalysis, LicenseAnalysis, Listing]:
        """
        Calls Gemini once with all images and returns all three analysis objects.
        Raises ValueError on any Gemini failure — does NOT silently return empty objects.
        """
        prompt = build_combined_analysis_prompt(
            platform=platform.value,
            description=description,
            product_name_hint=product_name_hint or "",
            product_material_hint=product_material_hint or "",
            height=height,
            width=width,
            weight=weight,
            dimension_unit=dimension_unit,
            weight_unit=weight_unit,
        )

        # Build list of image paths to pass in a single call
        image_paths = []
        if product_image_paths:
            image_paths.extend(product_image_paths)
            logger.info("%d product images included", len(product_image_paths))
        else:
            logger.warning("No product images provided — none will be sent to Gemini")

        if license_image_path:
            image_paths.append(license_image_path)
            logger.info("license_image_path included: %s", license_image_path)
        else:
            logger.warning("license_image_path is None — no license image will be sent to Gemini")

        logger.info(
            "CombinedAnalysisService: calling Gemini with %d image(s)", len(image_paths)
        )

        # This will raise ValueError on any failure — no silent empty dict
        raw: Dict[str, Any] = await self.client.generate_json(
            prompt, image_paths=image_paths if image_paths else None
        )

        logger.info("Combined Gemini response keys: %s", list(raw.keys()))

        # --- Unpack product_analysis ---
        raw_product = raw.get("product_analysis")
        if not raw_product or not isinstance(raw_product, dict):
            logger.error(
                "Combined Gemini response missing 'product_analysis' key. Full response: %s", raw
            )
            raise ValueError(
                f"Gemini combined response missing 'product_analysis'. Got keys: {list(raw.keys())}"
            )

        logger.info("product_analysis from Gemini: %s", raw_product)
        product_analysis = ProductAnalysis.model_validate(raw_product)
        product_analysis.platform = platform

        if not product_analysis.identified_product:
            logger.error(
                "product_analysis.identified_product is empty after parsing. raw_product=%s",
                raw_product,
            )
            raise ValueError(
                f"Gemini returned an empty 'identified_product'. raw_product: {raw_product}"
            )

        # --- Unpack license_analysis ---
        raw_license = raw.get("license_analysis")
        if not raw_license or not isinstance(raw_license, dict):
            logger.error(
                "Combined Gemini response missing 'license_analysis'. Full response: %s", raw
            )
            raise ValueError(
                f"Gemini combined response missing 'license_analysis'. Got keys: {list(raw.keys())}"
            )

        logger.info("license_analysis from Gemini: %s", raw_license)
        license_analysis = LicenseAnalysis.model_validate(raw_license)

        # --- Unpack listing ---
        raw_listing = raw.get("listing")
        if not raw_listing or not isinstance(raw_listing, dict):
            logger.error(
                "Combined Gemini response missing 'listing'. Full response: %s", raw
            )
            raise ValueError(
                f"Gemini combined response missing 'listing'. Got keys: {list(raw.keys())}"
            )

        logger.info("listing from Gemini: %s", raw_listing)
        listing = Listing.model_validate(raw_listing)

        return product_analysis, license_analysis, listing

import json
from typing import Any, Dict

from app.core.logging import get_logger
from app.schemas.listing import Listing
from app.schemas.platform_rules import PlatformEnum
from app.services.gemini.client import GeminiClient
from app.services.gemini.prompt_builder import build_listing_prompt

logger = get_logger(__name__)


class ListingService:
    def __init__(self, client: GeminiClient | None = None) -> None:
        self.client = client or GeminiClient()

    async def generate_listing(
        self,
        platform: PlatformEnum,
        product_analysis: dict,
        license_analysis: dict,
        packaging_info: dict,
    ) -> Listing:
        if not product_analysis or not product_analysis.get("identified_product"):
            logger.warning("Empty product_analysis received. Skipping generative listing creation.")
            return Listing()

        prompt = build_listing_prompt(
            platform=platform.value,
            product_analysis_json=json.dumps(product_analysis, ensure_ascii=False, indent=2),
            license_analysis_json=json.dumps(license_analysis, ensure_ascii=False, indent=2),
            packaging_info_json=json.dumps(packaging_info, ensure_ascii=False, indent=2),
        )

        logger.info("Sending listing generation prompt to Gemini")
        raw: Dict[str, Any] = await self.client.generate_json(prompt)
        logger.info("Raw listing response: %s", raw)

        listing = Listing.model_validate(raw)
        return listing
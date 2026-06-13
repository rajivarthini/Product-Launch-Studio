from typing import Any, Dict, Optional

from app.schemas.packaging import PackagingInfo
from app.services.gemini.client import GeminiClient
from app.services.gemini.prompt_builder import build_packaging_design_prompt
from app.core.logging import get_logger

logger = get_logger(__name__)


class PackagingDesignService:
    def __init__(self, client: GeminiClient | None = None) -> None:
        self.client = client or GeminiClient()

    async def generate_design(
        self,
        packaging_context: Dict[str, Any],
    ) -> PackagingInfo:
        prompt = build_packaging_design_prompt(
            packaging_context_json=packaging_context
        )
        raw: Dict[str, Any] = await self.client.generate_json(prompt)

        try:
            packaging = PackagingInfo(**raw)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to validate packaging info: %s", exc)
            packaging = PackagingInfo(
                recommended_packaging_type=raw.get(
                    "recommended_packaging_type", ""
                ),
                packaging_material=raw.get("packaging_material", ""),
            )
        return packaging

    async def generate_mockup_image(
        self,
        packaging_description: str,
        original_product_image_url: str,
    ) -> Optional[str]:
        # TODO: Implement Gemini image generation for packaging mockups.
        # This should respect the constraint of not creating new product angles.
        return None


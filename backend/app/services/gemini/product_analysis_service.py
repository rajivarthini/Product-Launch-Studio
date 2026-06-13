from typing import Any, Dict

from app.core.logging import get_logger
from app.schemas.platform_rules import PlatformEnum
from app.schemas.product import ProductAnalysis
from app.services.gemini.client import GeminiClient
from app.services.gemini.prompt_builder import build_product_analysis_prompt

logger = get_logger(__name__)


class ProductAnalysisService:
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
        product_image_path: str | None = None,
    ) -> ProductAnalysis:
        prompt = build_product_analysis_prompt(
            description=description,
            platform=platform.value,
            height=height,
            width=width,
            weight=weight,
            dimension_unit=dimension_unit,
            weight_unit=weight_unit,
            product_name_hint=product_name_hint or "",
            product_material_hint=product_material_hint or "",
        )

        logger.info("Sending product analysis prompt to Gemini")
        raw: Dict[str, Any] = await self.client.generate_json(prompt, image_path=product_image_path)
        logger.info("Raw product analysis response: %s", raw)

        analysis = ProductAnalysis.model_validate(raw)

        analysis.platform = platform
        return analysis
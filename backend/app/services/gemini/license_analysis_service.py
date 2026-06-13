from typing import Any, Dict

from app.core.logging import get_logger
from app.schemas.license import LicenseAnalysis
from app.services.gemini.client import GeminiClient
from app.services.gemini.prompt_builder import build_license_analysis_prompt

logger = get_logger(__name__)


class LicenseAnalysisService:
    def __init__(self, client: GeminiClient | None = None) -> None:
        self.client = client or GeminiClient()

    async def analyze(
        self,
        extracted_text: str,
        product_description: str,
        license_image_path: str | None = None,
    ) -> LicenseAnalysis:
        prompt = build_license_analysis_prompt(
            extracted_text=extracted_text or "",
            product_description=product_description or "",
        )

        if license_image_path:
            prompt += "\n\nPlease extract any visible text from the attached license image and assess its compliance information."

        logger.info("Sending license analysis prompt to Gemini")
        raw: Dict[str, Any] = await self.client.generate_json(prompt, image_path=license_image_path)
        logger.info("Raw license analysis response: %s", raw)

        analysis = LicenseAnalysis.model_validate(raw)
        return analysis
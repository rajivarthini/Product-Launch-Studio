from typing import Any

import httpx

from app.schemas.packaging import PackagingInfo
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DielineService:
    async def generate_dieline_payload(
        self, packaging_info: PackagingInfo
    ) -> dict:
        """
        Integrate with TemplateMaker (templatemaker.nl) if configured.

        - Uses TEMPLATEMAKER_BASE_URL from settings as the endpoint.
        - Sends a minimal JSON payload with type, material and dimensions.
        - Returns the raw response JSON when available.
        - On any error or missing config, returns a simple local payload.
        """
        base_url = settings.TEMPLATEMAKER_BASE_URL

        payload: dict[str, Any] = {
            "type": packaging_info.recommended_packaging_type,
            "material": packaging_info.packaging_material,
            "dimensions": packaging_info.packaging_dimensions.dict(),
            "notes": packaging_info.design_notes,
        }

        if not base_url:
            logger.info(
                "TEMPLATEMAKER_BASE_URL not configured; returning local dieline payload."
            )
            payload["template_source"] = "local_mock"
            return payload

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(base_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                data.setdefault("template_source", "templatemaker")
                return data
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "TemplateMaker integration failed, using fallback payload: %s", exc
            )
            payload["template_source"] = "templatemaker_fallback"
            return payload


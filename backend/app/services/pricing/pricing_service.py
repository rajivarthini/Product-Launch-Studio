from __future__ import annotations

from typing import Any

from serpapi import GoogleSearch

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.pricing import PricingInfo, PriceRange, Competitor
from app.schemas.product import ProductAnalysis

logger = get_logger(__name__)


class PricingService:
    def __init__(self) -> None:
        self.api_key = settings.SERPAPI_API_KEY

    def _parse_price(self, price_str: str) -> float:
        # Very small, defensive parser for prices like "₹1,299.00"
        digits = "".join(ch for ch in price_str if ch.isdigit() or ch == ".")
        try:
            return float(digits)
        except ValueError:
            return 0.0

    def estimate(
        self,
        product_analysis: ProductAnalysis,
        description: str = "",
        platform: Any = None,
    ) -> PricingInfo:
        """
        Minimal pricing aggregation using SerpAPI.
        - Focuses on Amazon India first via Google Shopping.
        - Returns a safe default structure on any error or missing configuration.
        """
        pricing = PricingInfo()

        if not self.api_key:
            logger.warning("SERPAPI_API_KEY not configured; returning default pricing.")
            return pricing

        product_name = (product_analysis.identified_product or "").strip()
        category = ""
        if product_analysis.category:
            category = (product_analysis.category.platform_category or "").strip()

        desc = description.strip()
        plat = platform.value if hasattr(platform, 'value') else str(platform or "")
        
        if product_name and category:
            query = f"{product_name} {category} {plat} india price".strip()
        elif product_name:
            query = f"{product_name} {plat} india price".strip()
        elif not product_name and desc:
            query = f"{desc} {plat} india price".strip()
        else:
            logger.info("No identified_product or description; skipping pricing lookup.")
            return pricing

        params: dict[str, Any] = {
            "engine": "google_shopping",
            "q": query,
            "api_key": self.api_key,
            "hl": "en",
            "gl": "in",
            "location": "India",
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
        except Exception as exc:  # noqa: BLE001
            logger.exception("SerpAPI request failed: %s", exc)
            return pricing

        shopping_results = results.get("shopping_results") or []
        
        # Rank by title keyword overlap with product_name/category
        def score_title(title: str) -> float:
            t_lower = title.lower()
            score = 0
            if product_name and product_name.lower() in t_lower:
                score += 10
            for word in product_name.lower().split():
                if len(word) > 2 and word in t_lower:
                    score += 1
            if category and category.lower() in t_lower:
                score += 3
            return score

        scored_results = [(r, score_title(r.get("title", ""))) for r in shopping_results]
        # Filter out anything with score 0 if we actually have a product_name
        if product_name:
            scored_results = [item for item in scored_results if item[1] > 0]
        
        scored_results.sort(key=lambda x: x[1], reverse=True)
        top_results = [item[0] for item in scored_results[:5]]

        competitors: list[Competitor] = []
        prices: list[float] = []

        for item in top_results:
            title = item.get("title") or ""
            price_str = item.get("price") or ""
            link = item.get("link") or ""
            source = item.get("source") or item.get("merchant") or "amazon.in"

            price_val = self._parse_price(price_str)
            if price_val <= 0:
                continue

            prices.append(price_val)
            competitors.append(
                Competitor(
                    title=title,
                    price=price_val,
                    source=str(source),
                    url=str(link),
                )
            )

        if prices:
            pricing.estimated_price_range = PriceRange(
                min=min(prices),
                max=max(prices),
            )
            pricing.example_competitors = competitors

        return pricing


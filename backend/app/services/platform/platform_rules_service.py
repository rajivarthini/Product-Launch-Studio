from app.core.constants import PLATFORM_DISCLAIMER
from app.schemas.platform_rules import PlatformEnum, PlatformRulesSummary
from app.core.logging import get_logger

logger = get_logger(__name__)


_PLATFORM_RULES_CONFIG: dict[PlatformEnum, PlatformRulesSummary] = {
    PlatformEnum.amazon: PlatformRulesSummary(
        image_rules=[
            "Use high-resolution images with clear focus on the product.",
            "Avoid added text or graphics that mislead about the product.",
            "Do not fabricate new or unseen product angles.",
        ],
        listing_rules=[
            "Include accurate title, brand, and key attributes.",
            "Avoid prohibited claims and ensure truthful information.",
        ],
        compliance_notes=[
            "Ensure product and packaging comply with applicable local regulations.",
            "Include valid license or certification details where required.",
        ],
        disclaimer=PLATFORM_DISCLAIMER,
    ),
    PlatformEnum.flipkart: PlatformRulesSummary(
        image_rules=[
            "Ensure product occupies major area of the image.",
            "Use clean, neutral background when possible.",
        ],
        listing_rules=[
            "Highlight key features and dimensions in bullet points.",
            "Avoid misleading pricing, discount, or offer language.",
        ],
        compliance_notes=[
            "Provide accurate compliance and license details as per category.",
        ],
        disclaimer=PLATFORM_DISCLAIMER,
    ),
    PlatformEnum.meesho: PlatformRulesSummary(
        image_rules=[
            "Use clear, realistic product images without filters that mislead.",
        ],
        listing_rules=[
            "Use concise titles and simple language suited to target buyers.",
        ],
        compliance_notes=[
            "Include relevant certification numbers where visible on packaging or labels.",
        ],
        disclaimer=PLATFORM_DISCLAIMER,
    ),
}


class PlatformRulesService:
    def get_rules(self, platform: PlatformEnum) -> PlatformRulesSummary:
        rules = _PLATFORM_RULES_CONFIG.get(platform)
        if not rules:
            logger.warning("No rules configured for platform %s", platform)
            rules = PlatformRulesSummary(
                image_rules=[],
                listing_rules=[],
                compliance_notes=[],
                disclaimer=PLATFORM_DISCLAIMER,
            )
        return rules


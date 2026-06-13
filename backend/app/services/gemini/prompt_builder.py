from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt file not found: %s", path)
        return ""


def _safe_replace(template: str, values: dict) -> str:
    """
    Replace only placeholders written as {{variable_name}}.
    This avoids breaking JSON examples inside prompt files.
    """
    result = template
    for key, value in values.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def build_product_analysis_prompt(**kwargs) -> str:
    tmpl = _load_prompt("product_analysis")
    return _safe_replace(tmpl, kwargs)


def build_license_analysis_prompt(**kwargs) -> str:
    tmpl = _load_prompt("license_analysis")
    return _safe_replace(tmpl, kwargs)


def build_listing_prompt(**kwargs) -> str:
    tmpl = _load_prompt("listing_generation")
    return _safe_replace(tmpl, kwargs)


def build_packaging_design_prompt(**kwargs) -> str:
    tmpl = _load_prompt("packaging_design")
    return _safe_replace(tmpl, kwargs)


def build_platform_rules_prompt(**kwargs) -> str:
    tmpl = _load_prompt("platform_rules")
    return _safe_replace(tmpl, kwargs)


def build_combined_analysis_prompt(**kwargs) -> str:
    tmpl = _load_prompt("combined_analysis")
    return _safe_replace(tmpl, kwargs)
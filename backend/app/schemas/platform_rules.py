from enum import Enum
from pydantic import BaseModel


class PlatformEnum(str, Enum):
    amazon = "amazon"
    flipkart = "flipkart"
    meesho = "meesho"


class PlatformRulesSummary(BaseModel):
    image_rules: list[str]
    listing_rules: list[str]
    compliance_notes: list[str]
    disclaimer: str


class PlatformInfo(BaseModel):
    selected: PlatformEnum
    rules_summary: PlatformRulesSummary


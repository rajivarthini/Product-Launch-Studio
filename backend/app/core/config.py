from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV: str = Field("development")
    DEBUG: bool = Field(True)

    # CORS – use plain str so Pydantic does not normalise/mangle URLs
    CORS_ALLOW_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
        ]
    )

    # Storage
    USE_CLOUDINARY: bool = Field(False)
    CLOUDINARY_CLOUD_NAME: str | None = Field(None)
    CLOUDINARY_API_KEY: str | None = Field(None)
    CLOUDINARY_API_SECRET: str | None = Field(None)
    LOCAL_UPLOAD_DIR: str = Field("uploads")

    # Gemini
    GEMINI_API_KEY: str | None = Field(None)
    GEMINI_API_BASE_URL: str = Field(
        "https://generativelanguage.googleapis.com/v1beta"
    )
    GEMINI_MODEL_NAME: str = Field("models/gemini-1.5-pro")
    GEMINI_IMAGE_MODEL_NAME: str = Field("models/gemini-1.5-flash")

    # Platform rules
    PLATFORM_RULES_VERSION: str = Field("2026-03")

    # LangChain / tracing
    LANGCHAIN_TRACING_V2: bool = Field(False)
    LANGCHAIN_API_KEY: str | None = Field(None)

    # SerpAPI
    SERPAPI_API_KEY: str | None = Field(None)

    # TemplateMaker
    TEMPLATEMAKER_BASE_URL: str | None = Field(None)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
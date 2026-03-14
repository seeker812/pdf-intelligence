from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PDF Intelligence API"
    app_env: str = "development"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./pdf_intelligence.db"

    cors_origins: list[str] = ["*"]

    openai_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache

def get_settings() -> Settings:
    return Settings()

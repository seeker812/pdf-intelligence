from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):

    APP_NAME: str = "PDF Intelligence API"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./pdf_intelligence.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    S3_BUCKET_NAME: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"

    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    QDRANT_PATH: str = "./qdrant_data"
    QDRANT_TIMEOUT: int = 30
    QDRANT_COLLECTION_NAME: str = "document_chunks"
    QDRANT_VECTOR_SIZE: int = 1536
    QDRANT_UPSERT_BATCH_SIZE: int = 100

    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / "backend" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, values: dict) -> dict:
        """Converts empty string env values to None so str | None fields work correctly."""
        return {
            k: None if isinstance(v, str) and v.strip() == "" else v
            for k, v in values.items()
        }

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: str) -> str:
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

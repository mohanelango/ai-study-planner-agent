from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "AI Study Planner Agent"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    FRONTEND_URL: str = "http://localhost:3000"

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/ai_study_planner"
    REDIS_URL: str = "redis://redis:6379/0"

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    QDRANT_URL: str = "http://qdrant:6333"

    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "study-documents"
    MINIO_SECURE: bool = False

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    JWT_SECRET_KEY: str = Field(default="change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

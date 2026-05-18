import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / f".env.{ENVIRONMENT}",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["dev", "test", "prod"] = ENVIRONMENT

    app_name: str = "BetYouCan"
    debug: bool = False

    google_client_id_web: str
    google_client_secret_web: str

    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field("HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(30, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_admin_api_key: Optional[str] = Field(None, alias="OPENAI_ADMIN_API_KEY")
    openai_org_id: Optional[str] = Field(None, alias="OPENAI_ORG_ID")
    openai_costs_api_url: str = Field(
        "https://api.openai.com/v1/organization/costs",
        alias="OPENAI_COSTS_API_URL",
    )
    serp_api_key: Optional[str] = Field(None, alias="SERP_API_KEY")
    serp_base_url: str = Field("https://serpapi.com/search.json", alias="SERP_BASE_URL")

    rabbitmq_url: str = Field(..., alias="RABBITMQ_URL")
    slowapi_redis_url: str = Field(..., alias="SLOWAPI_REDIS_URL")

    aws_region: str = Field(..., alias="AWS_REGION")
    s3_bucket: str = Field(..., alias="S3_BUCKET")
    aws_access_key: str = Field(..., alias="AWS_ACCESS_KEY")
    aws_secret_key: str = Field(..., alias="AWS_SECRET_KEY")

    stripe_secret_key: str = Field(..., alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(..., alias="STRIPE_WEBHOOK_SECRET")

    ses_access_key: str = Field(..., alias="SES_ACCESS_KEY")
    ses_secret_key: str = Field(..., alias="SES_SECRET_KEY")
    sender_email: str = Field(..., alias="SENDER_EMAIL")

    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(..., alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(..., alias="POSTGRES_DB")

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

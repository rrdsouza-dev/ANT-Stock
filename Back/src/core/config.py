from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "ANT Stock API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"

    database_url: SecretStr = Field(
        default=SecretStr("postgresql+asyncpg://postgres:postgres@localhost:5432/ant_stock"),
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    celery_broker_url: str | None = Field(default=None, validation_alias="CELERY_BROKER_URL")
    celery_result_backend: str | None = Field(default=None, validation_alias="CELERY_RESULT_BACKEND")

    jwt_secret_key: SecretStr = Field(
        default=SecretStr("troque-esta-chave-em-producao"),
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=60,
        validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    cors_origins: list[AnyHttpUrl] | list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        validation_alias="CORS_ORIGINS",
    )

    rate_limit_window_seconds: int = Field(default=60, validation_alias="RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_auth_attempts: int = Field(default=8, validation_alias="RATE_LIMIT_AUTH_ATTEMPTS")
    rate_limit_block_seconds: int = Field(default=120, validation_alias="RATE_LIMIT_BLOCK_SECONDS")

    @property
    def url_banco(self) -> str:
        return self.database_url.get_secret_value()

    @property
    def broker_celery(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def backend_celery(self) -> str:
        return self.celery_result_backend or self.redis_url


@lru_cache
def config() -> Settings:
    return Settings()

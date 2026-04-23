from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str | None = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_key: SecretStr | None = Field(
        default=None,
        validation_alias="SUPABASE_KEY",
    )
    supabase_schema: str = Field(
        default="public",
        validation_alias="SUPABASE_SCHEMA",
    )
    supabase_timeout_seconds: int = Field(
        default=10,
        validation_alias="SUPABASE_TIMEOUT_SECONDS",
    )

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()

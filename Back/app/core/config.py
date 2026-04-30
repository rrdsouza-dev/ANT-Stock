from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Centraliza as variaveis do .env usadas pelo backend.
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
    auth_google_redirect: str | None = Field(
        default=None,
        validation_alias="AUTH_GOOGLE_REDIRECT",
    )
    auth_google_scopes: str = Field(
        default="openid email profile",
        validation_alias="AUTH_GOOGLE_SCOPES",
    )
    jwt_chave: str = Field(
        default="troque-esta-chave-em-producao",
        validation_alias="JWT_CHAVE",
    )
    jwt_algoritmo: str = Field(
        default="HS256",
        validation_alias="JWT_ALGORITMO",
    )
    jwt_expira_minutos: int = Field(
        default=60,
        validation_alias="JWT_EXPIRA_MINUTOS",
    )
    rate_limite_janela_segundos: int = Field(
        default=60,
        validation_alias="RATE_LIMITE_JANELA_SEGUNDOS",
    )
    rate_limite_auth_tentativas: int = Field(
        default=8,
        validation_alias="RATE_LIMITE_AUTH_TENTATIVAS",
    )
    rate_limite_bloqueio_segundos: int = Field(
        default=120,
        validation_alias="RATE_LIMITE_BLOQUEIO_SEGUNDOS",
    )
    rate_limite_peso_identidade: bool = Field(
        default=True,
        validation_alias="RATE_LIMITE_PESO_IDENTIDADE",
    )

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)


@lru_cache
def obter_config() -> Settings:
    # Evita reler o .env a cada chamada.
    return Settings()

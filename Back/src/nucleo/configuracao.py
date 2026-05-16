from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ_BACKEND = Path(__file__).resolve().parents[2]


class Configuracoes(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=RAIZ_BACKEND / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    nome_app: str = Field(default="ANT API", validation_alias="APP_NAME")
    versao_app: str = Field(default="1.0.0", validation_alias="APP_VERSION")
    ambiente: str = Field(default="development", validation_alias="ENVIRONMENT")
    depurar: bool = Field(default=False, validation_alias="DEBUG")
    prefixo_api: str = Field(default="/api/v1", validation_alias="API_PREFIX")

    url_banco_dados: SecretStr = Field(
        default=SecretStr("postgresql+asyncpg://postgres:postgres@localhost:5432/ant_stock"),
        validation_alias="DATABASE_URL",
    )
    supabase_url: AnyHttpUrl | None = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_anon_key: SecretStr | None = Field(default=None, validation_alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: SecretStr | None = Field(default=None, validation_alias="SUPABASE_SERVICE_ROLE_KEY")

    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    celery_broker_url: str | None = Field(default=None, validation_alias="CELERY_BROKER_URL")
    celery_result_backend: str | None = Field(default=None, validation_alias="CELERY_RESULT_BACKEND")

    jwt_chave: SecretStr = Field(
        default=SecretStr("troque-esta-chave-em-producao"),
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algoritmo: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_expira_minutos: int = Field(default=60, validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    origens_cors: list[AnyHttpUrl] | list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        validation_alias="CORS_ORIGINS",
    )

    janela_limite_segundos: int = Field(default=60, validation_alias="RATE_LIMIT_WINDOW_SECONDS")
    tentativas_auth_limite: int = Field(default=8, validation_alias="RATE_LIMIT_AUTH_ATTEMPTS")
    bloqueio_limite_segundos: int = Field(default=120, validation_alias="RATE_LIMIT_BLOCK_SECONDS")

    @property
    def url_banco(self) -> str:
        return self.url_banco_dados.get_secret_value()

    @property
    def broker_celery(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def backend_celery(self) -> str:
        return self.celery_result_backend or self.redis_url


@lru_cache
def configuracao() -> Configuracoes:
    return Configuracoes()

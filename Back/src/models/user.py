# Modelo de usuario da aplicacao.
from uuid import UUID

from sqlmodel import Field

from src.models.base import TimestampMixin, UserProfile, UUIDMixin


class User(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "usuarios"

    email: str = Field(unique=True, index=True, max_length=255)
    name: str | None = Field(default=None, alias="nome", max_length=120)
    password_hash: str = Field(alias="senha_hash", max_length=255)
    provider: str | None = Field(default="local", alias="provedor", max_length=40)
    profile: UserProfile | None = Field(default=None, alias="perfil")
    scope_id: UUID | None = Field(default=None, alias="escopo_id", foreign_key="escopos.id")
    active: bool = Field(default=True, alias="ativo")

# Modelo de escopo organizacional do estoque.
from uuid import UUID

from sqlmodel import Field

from src.models.base import ScopeType, TimestampMixin, UUIDMixin


class Scope(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "escopos"

    name: str = Field(alias="nome", max_length=120)
    scope_type: ScopeType = Field(alias="tipo", index=True)
    school_id: UUID | None = Field(default=None, alias="escola_id")
    class_id: UUID | None = Field(default=None, alias="turma_id")
    active: bool = Field(default=True, alias="ativo")

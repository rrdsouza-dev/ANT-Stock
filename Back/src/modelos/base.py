from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class PerfilCodigo(StrEnum):
    ALUNO = "aluno"
    PROFESSOR = "professor"
    GESTAO = "gestao"


class TipoMovimentacao(StrEnum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class StatusPedido(StrEnum):
    ABERTO = "aberto"
    SEPARADO = "separado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


def agora_utc() -> datetime:
    return datetime.now(UTC)


class DatasMixin(SQLModel):
    criado_em: datetime = Field(default_factory=agora_utc, nullable=False)
    atualizado_em: datetime = Field(default_factory=agora_utc, nullable=False)


class IdMixin(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

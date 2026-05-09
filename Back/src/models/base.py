from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ScopeType(StrEnum):
    SCHOOL_MANAGEMENT = "gestao_escola"
    LOGISTICS_CLASS = "turma_logistica"


class MovementType(StrEnum):
    IN = "entrada"
    OUT = "saida"


class UserProfile(StrEnum):
    MANAGEMENT = "gestao"
    TEACHER = "professor"
    STUDENT = "aluno"


def utcnow() -> datetime:
    return datetime.now(UTC)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)


class UUIDMixin(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

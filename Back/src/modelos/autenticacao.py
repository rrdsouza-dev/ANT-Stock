from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Column, Field, Relationship, SQLModel, String

from src.modelos.base import DatasMixin, IdMixin, PerfilCodigo, agora_utc

if TYPE_CHECKING:
    from src.modelos.estoque import Deposito, Movimentacao
    from src.modelos.pedido import Pedido


# Reutilizado em todas as colunas que referenciam o tipo perfil_codigo do PostgreSQL.
# values_callable garante que o SQLAlchemy use o .value do StrEnum ("gestao")
# em vez do .name ("GESTAO"), evitando o erro:
#   invalid input value for enum perfil_codigo: "GESTAO"
def _enum_perfil() -> SAEnum:
    return SAEnum(
        PerfilCodigo,
        name="perfil_codigo",
        create_type=False,
        values_callable=lambda e: [m.value for m in e],
    )


class Perfil(IdMixin, DatasMixin, table=True):
    __tablename__ = "perfis"  # type: ignore[assignment]

    codigo: PerfilCodigo = Field(sa_column=Column(_enum_perfil(), nullable=False, unique=True, index=True))
    nome: str = Field(max_length=40)

    usuarios: list["Usuario"] = Relationship(back_populates="perfil")


class UsuarioDeposito(SQLModel, table=True):
    __tablename__ = "usuario_depositos"  # type: ignore[assignment]
    __table_args__ = (PrimaryKeyConstraint("usuario_id", "deposito_id"),)  # type: ignore[assignment]

    usuario_id: UUID = Field(foreign_key="usuarios.id", index=True)
    deposito_id: UUID = Field(foreign_key="depositos.id", index=True)
    criado_em: datetime = Field(default_factory=agora_utc, nullable=False)


class Usuario(IdMixin, DatasMixin, table=True):
    __tablename__ = "usuarios"  # type: ignore[assignment]

    auth_id: UUID | None = Field(default=None, unique=True, index=True)
    email: str = Field(unique=True, index=True, max_length=255)
    nome: str | None = Field(default=None, max_length=120)
    senha_hash: str | None = Field(default=None, max_length=255)
    provedor: str = Field(default="local", max_length=40)
    perfil_id: UUID = Field(foreign_key="perfis.id", index=True)
    # Turmas do professor (ex: ["2A", "3A"]). Vazio para perfis que nao sao professor.
    turmas: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String(30)), nullable=False, server_default="{}"),
    )
    ativo: bool = Field(default=True)

    perfil: Perfil | None = Relationship(back_populates="usuarios")
    depositos: list["Deposito"] = Relationship(back_populates="usuarios", link_model=UsuarioDeposito)
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")
    movimentacoes: list["Movimentacao"] = Relationship(back_populates="usuario")
    codigos_recuperacao: list["CodigoRecuperacao"] = Relationship(back_populates="usuario")


class CodigoRecuperacao(IdMixin, DatasMixin, table=True):
    __tablename__ = "codigos_recuperacao"  # type: ignore[assignment]

    usuario_id: UUID = Field(foreign_key="usuarios.id", index=True)
    codigo_hash: str = Field(max_length=128, index=True)
    expira_em: datetime = Field(nullable=False)
    usado: bool = Field(default=False)
    tentativas: int = Field(default=0, ge=0)
    bloqueado_ate: datetime | None = Field(default=None)

    usuario: Usuario | None = Relationship(back_populates="codigos_recuperacao")

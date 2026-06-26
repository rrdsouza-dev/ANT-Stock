from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import PrimaryKeyConstraint
from sqlmodel import Column, Field, Relationship, SQLModel

from src.modelos.base import DatasMixin, IdMixin, PerfilCodigo, StatusCadastro, agora_utc

if TYPE_CHECKING:
    from src.modelos.estoque import Deposito, Movimentacao
    from src.modelos.pedido import Pedido


class Perfil(IdMixin, DatasMixin, table=True):
    __tablename__ = "perfis"  # type: ignore[assignment]

    # name="perfil_codigo" matches the PostgreSQL type created in the migration.
    # create_type=False tells SQLAlchemy NOT to issue CREATE TYPE — it already exists.
    codigo: PerfilCodigo = Field(
        sa_column=Column(
            SAEnum(PerfilCodigo, name="perfil_codigo", create_type=False),
            nullable=False,
            unique=True,
            index=True,
        )
    )
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
    sala: str | None = Field(default=None, max_length=30)
    ativo: bool = Field(default=True)

    perfil: Perfil | None = Relationship(back_populates="usuarios")
    depositos: list["Deposito"] = Relationship(back_populates="usuarios", link_model=UsuarioDeposito)
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")
    movimentacoes: list["Movimentacao"] = Relationship(back_populates="usuario")
    codigos_recuperacao: list["CodigoRecuperacao"] = Relationship(back_populates="usuario")


class CadastroPendente(IdMixin, DatasMixin, table=True):
    __tablename__ = "cadastro_pendente"  # type: ignore[assignment]

    nome: str = Field(min_length=2, max_length=120)
    email: str = Field(unique=True, index=True, max_length=255)
    senha_hash: str = Field(max_length=255)
    perfil_solicitado: PerfilCodigo = Field(
        sa_column=Column(
            SAEnum(PerfilCodigo, name="perfil_codigo", create_type=False),
            nullable=False,
            index=True,
        )
    )
    status: StatusCadastro = Field(
        sa_column=Column(
            SAEnum(StatusCadastro, name="status_cadastro", create_type=False),
            nullable=False,
            default=StatusCadastro.PENDENTE,
            index=True,
        )
    )


class HistoricoAprovacao(IdMixin, DatasMixin, table=True):
    __tablename__ = "historico_aprovacoes"  # type: ignore[assignment]

    usuario_id: UUID = Field(foreign_key="usuarios.id", index=True)
    nome: str = Field(max_length=120)
    email: str = Field(max_length=255, index=True)
    perfil: PerfilCodigo = Field(
        sa_column=Column(
            SAEnum(PerfilCodigo, name="perfil_codigo", create_type=False),
            nullable=False,
            index=True,
        )
    )
    aprovado_por_id: UUID = Field(foreign_key="usuarios.id", index=True)


class HistoricoRecusa(IdMixin, DatasMixin, table=True):
    __tablename__ = "historico_recusas"  # type: ignore[assignment]

    nome: str = Field(max_length=120)
    email: str = Field(max_length=255, index=True)
    perfil_solicitado: PerfilCodigo = Field(
        sa_column=Column(
            SAEnum(PerfilCodigo, name="perfil_codigo", create_type=False),
            nullable=False,
            index=True,
        )
    )
    recusado_por_id: UUID = Field(foreign_key="usuarios.id", index=True)
    motivo: str | None = Field(default=None, max_length=500)


class CodigoRecuperacao(IdMixin, DatasMixin, table=True):
    __tablename__ = "codigos_recuperacao"  # type: ignore[assignment]

    usuario_id: UUID = Field(foreign_key="usuarios.id", index=True)
    codigo_hash: str = Field(max_length=128, index=True)
    expira_em: datetime = Field(nullable=False)
    usado: bool = Field(default=False)
    tentativas: int = Field(default=0, ge=0)
    bloqueado_ate: datetime | None = Field(default=None)

    usuario: Usuario | None = Relationship(back_populates="codigos_recuperacao")

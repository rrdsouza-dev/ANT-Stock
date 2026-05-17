from datetime import datetime
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint
from sqlmodel import Field, Relationship, SQLModel

from src.modelos.base import DatasMixin, IdMixin, PerfilCodigo, agora_utc

if TYPE_CHECKING:
    from src.modelos.estoque import Deposito, Movimentacao
    from src.modelos.pedido import Pedido


class Perfil(IdMixin, DatasMixin, table=True):
    __tablename__: ClassVar[str] = "perfis"

    codigo: PerfilCodigo = Field(unique=True, index=True)
    nome: str = Field(max_length=40)

    usuarios: list["Usuario"] = Relationship(back_populates="perfil")


class UsuarioDeposito(SQLModel, table=True):
    __tablename__: ClassVar[str] = "usuario_depositos"
    __table_args__: ClassVar[tuple[PrimaryKeyConstraint]] = (PrimaryKeyConstraint("usuario_id", "deposito_id"),)

    usuario_id: UUID = Field(foreign_key="usuarios.id", index=True)
    deposito_id: UUID = Field(foreign_key="depositos.id", index=True)
    criado_em: datetime = Field(default_factory=agora_utc, nullable=False)


class Usuario(IdMixin, DatasMixin, table=True):
    __tablename__: ClassVar[str] = "usuarios"

    auth_id: UUID | None = Field(default=None, unique=True, index=True) 
    email: str = Field(unique=True, index=True, max_length=255)
    nome: str | None = Field(default=None, max_length=120)
    senha_hash: str | None = Field(default=None, max_length=255)
    provedor: str = Field(default="local", max_length=40)
    perfil_id: UUID = Field(foreign_key="perfis.id", index=True)
    ativo: bool = Field(default=True)

    perfil: Perfil | None = Relationship(back_populates="usuarios")
    depositos: list["Deposito"] = Relationship(back_populates="usuarios", link_model=UsuarioDeposito)
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")
    movimentacoes: list["Movimentacao"] = Relationship(back_populates="usuario")

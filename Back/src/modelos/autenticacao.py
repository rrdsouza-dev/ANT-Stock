from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from src.modelos.base import DatasMixin, IdMixin, PerfilCodigo

if TYPE_CHECKING:
    from src.modelos.estoque import Movimentacao
    from src.modelos.pedido import Pedido


class Perfil(IdMixin, DatasMixin, table=True):
    __tablename__ = "perfis"

    codigo: PerfilCodigo = Field(unique=True, index=True)
    nome: str = Field(max_length=40)

    usuarios: list["Usuario"] = Relationship(back_populates="perfil")


class Usuario(IdMixin, DatasMixin, table=True):
    __tablename__ = "usuarios"

    auth_id: UUID | None = Field(default=None, unique=True, index=True) 
    email: str = Field(unique=True, index=True, max_length=255)
    nome: str | None = Field(default=None, max_length=120)
    senha_hash: str | None = Field(default=None, max_length=255)
    provedor: str = Field(default="local", max_length=40)
    perfil_id: UUID = Field(foreign_key="perfis.id", index=True)
    ativo: bool = Field(default=True)

    perfil: Perfil | None = Relationship(back_populates="usuarios")
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")
    movimentacoes: list["Movimentacao"] = Relationship(back_populates="usuario")

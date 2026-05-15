from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.modelos.base import DatasMixin, IdMixin, TipoMovimentacao, agora_utc

if TYPE_CHECKING:
    from src.modelos.autenticacao import Usuario
    from src.modelos.pedido import ItemPedido, Pedido


class Categoria(IdMixin, DatasMixin, table=True):
    __tablename__ = "categorias"

    nome: str = Field(min_length=1, max_length=120, unique=True, index=True)
    descricao: str | None = Field(default=None, max_length=500)
    ativo: bool = Field(default=True)

    produtos: list["Produto"] = Relationship(back_populates="categoria")


class Localizacao(IdMixin, DatasMixin, table=True):
    __tablename__ = "localizacoes"

    nome: str = Field(min_length=1, max_length=120, unique=True, index=True)
    corredor: str | None = Field(default=None, max_length=50)
    prateleira: str | None = Field(default=None, max_length=50)
    posicao: str | None = Field(default=None, max_length=50)
    ativo: bool = Field(default=True)

    produtos: list["Produto"] = Relationship(back_populates="localizacao")
    saldos: list["Estoque"] = Relationship(back_populates="localizacao")


class Produto(IdMixin, DatasMixin, table=True):
    __tablename__ = "produtos"

    nome: str = Field(min_length=1, max_length=160, index=True)
    codigo: str | None = Field(default=None, unique=True, max_length=80, index=True)
    categoria_id: UUID | None = Field(default=None, foreign_key="categorias.id", index=True)
    localizacao_id: UUID | None = Field(default=None, foreign_key="localizacoes.id", index=True)
    quantidade_minima: int = Field(default=0, ge=0)
    ativo: bool = Field(default=True)

    categoria: Categoria | None = Relationship(back_populates="produtos")
    localizacao: Localizacao | None = Relationship(back_populates="produtos")
    saldos: list["Estoque"] = Relationship(back_populates="produto")
    movimentacoes: list["Movimentacao"] = Relationship(back_populates="produto")
    itens_pedido: list["ItemPedido"] = Relationship(back_populates="produto")


class Estoque(IdMixin, DatasMixin, table=True):
    __tablename__ = "estoque"
    __table_args__ = (UniqueConstraint("produto_id", "localizacao_id", name="uq_estoque_produto_local"),)

    produto_id: UUID = Field(foreign_key="produtos.id", index=True)
    localizacao_id: UUID | None = Field(default=None, foreign_key="localizacoes.id", index=True)
    quantidade: int = Field(default=0, ge=0)

    produto: Produto | None = Relationship(back_populates="saldos")
    localizacao: Localizacao | None = Relationship(back_populates="saldos")


class Movimentacao(IdMixin, DatasMixin, table=True):
    __tablename__ = "movimentacoes"

    produto_id: UUID = Field(foreign_key="produtos.id", index=True)
    usuario_id: UUID | None = Field(default=None, foreign_key="usuarios.id", index=True)
    pedido_id: UUID | None = Field(default=None, foreign_key="pedidos.id", index=True)
    origem_id: UUID | None = Field(default=None, foreign_key="localizacoes.id", index=True)
    destino_id: UUID | None = Field(default=None, foreign_key="localizacoes.id", index=True)
    tipo: TipoMovimentacao = Field(index=True)
    quantidade: int = Field(gt=0)
    observacao: str | None = Field(default=None, max_length=500)
    movimentado_em: datetime = Field(default_factory=agora_utc)

    produto: Produto | None = Relationship(back_populates="movimentacoes")
    usuario: Optional["Usuario"] = Relationship(back_populates="movimentacoes")
    pedido: Optional["Pedido"] = Relationship(back_populates="movimentacoes")

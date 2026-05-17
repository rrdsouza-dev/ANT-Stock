from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.modelos.autenticacao import UsuarioDeposito
from src.modelos.base import DatasMixin, IdMixin, TipoDeposito, TipoMovimentacao, agora_utc

if TYPE_CHECKING:
    from src.modelos.autenticacao import Usuario
    from src.modelos.pedido import ItemPedido, Pedido


class Deposito(IdMixin, DatasMixin, table=True):
    __tablename__: ClassVar[str] = "depositos"

    nome: str = Field(min_length=1, max_length=120, unique=True, index=True)
    tipo: TipoDeposito = Field(index=True)
    descricao: str | None = Field(default=None, max_length=500)
    ativo: bool = Field(default=True)

    categorias: list["Categoria"] = Relationship(back_populates="deposito")
    localizacoes: list["Localizacao"] = Relationship(back_populates="deposito")
    produtos: list["Produto"] = Relationship(back_populates="deposito")
    estoques: list["Estoque"] = Relationship(back_populates="deposito")
    movimentacoes: list["Movimentacao"] = Relationship(back_populates="deposito")
    pedidos: list["Pedido"] = Relationship(back_populates="deposito")
    itens_pedido: list["ItemPedido"] = Relationship(back_populates="deposito")
    usuarios: list["Usuario"] = Relationship(back_populates="depositos", link_model=UsuarioDeposito)


class Categoria(IdMixin, DatasMixin, table=True):
    __tablename__: ClassVar[str] = "categorias"

    deposito_id: UUID = Field(foreign_key="depositos.id", index=True)
    nome: str = Field(min_length=1, max_length=120, index=True)
    descricao: str | None = Field(default=None, max_length=500)
    ativo: bool = Field(default=True)

    deposito: Deposito | None = Relationship(back_populates="categorias")
    produtos: list["Produto"] = Relationship(back_populates="categoria")


class Localizacao(IdMixin, DatasMixin, table=True):
    __tablename__: ClassVar[str] = "localizacoes"

    deposito_id: UUID = Field(foreign_key="depositos.id", index=True)
    nome: str = Field(min_length=1, max_length=120, index=True)
    corredor: str | None = Field(default=None, max_length=50)
    prateleira: str | None = Field(default=None, max_length=50)
    posicao: str | None = Field(default=None, max_length=50)
    ativo: bool = Field(default=True)

    deposito: Deposito | None = Relationship(back_populates="localizacoes")
    produtos: list["Produto"] = Relationship(back_populates="localizacao")
    saldos: list["Estoque"] = Relationship(back_populates="localizacao")


class Produto(IdMixin, DatasMixin, table=True):
    __tablename__: ClassVar[str] = "produtos"

    deposito_id: UUID = Field(foreign_key="depositos.id", index=True)
    nome: str = Field(min_length=1, max_length=160, index=True)
    codigo: str | None = Field(default=None, max_length=80, index=True)
    categoria_id: UUID | None = Field(default=None, foreign_key="categorias.id", index=True)
    localizacao_id: UUID | None = Field(default=None, foreign_key="localizacoes.id", index=True)
    quantidade_minima: int = Field(default=0, ge=0)
    ativo: bool = Field(default=True)

    deposito: Deposito | None = Relationship(back_populates="produtos")
    categoria: Categoria | None = Relationship(back_populates="produtos")
    localizacao: Localizacao | None = Relationship(back_populates="produtos")
    saldos: list["Estoque"] = Relationship(back_populates="produto")
    movimentacoes: list["Movimentacao"] = Relationship(back_populates="produto")
    itens_pedido: list["ItemPedido"] = Relationship(back_populates="produto")


class Estoque(IdMixin, DatasMixin, table=True):
    __tablename__: ClassVar[str] = "estoque"
    __table_args__: ClassVar[tuple[UniqueConstraint]] = (
        UniqueConstraint("deposito_id", "produto_id", "localizacao_id", name="uq_estoque_deposito_produto_local"),
    )

    deposito_id: UUID = Field(foreign_key="depositos.id", index=True)
    produto_id: UUID = Field(foreign_key="produtos.id", index=True)
    localizacao_id: UUID | None = Field(default=None, foreign_key="localizacoes.id", index=True)
    quantidade: int = Field(default=0, ge=0)

    deposito: Deposito | None = Relationship(back_populates="estoques")
    produto: Produto | None = Relationship(back_populates="saldos")
    localizacao: Localizacao | None = Relationship(back_populates="saldos")


class Movimentacao(IdMixin, DatasMixin, table=True):
    __tablename__: ClassVar[str] = "movimentacoes"

    deposito_id: UUID = Field(foreign_key="depositos.id", index=True)
    produto_id: UUID = Field(foreign_key="produtos.id", index=True)
    usuario_id: UUID | None = Field(default=None, foreign_key="usuarios.id", index=True)
    pedido_id: UUID | None = Field(default=None, foreign_key="pedidos.id", index=True)
    origem_id: UUID | None = Field(default=None, foreign_key="localizacoes.id", index=True)
    destino_id: UUID | None = Field(default=None, foreign_key="localizacoes.id", index=True)
    tipo: TipoMovimentacao = Field(index=True)
    quantidade: int = Field(gt=0)
    observacao: str | None = Field(default=None, max_length=500)
    movimentado_em: datetime = Field(default_factory=agora_utc)

    deposito: Deposito | None = Relationship(back_populates="movimentacoes")
    produto: Produto | None = Relationship(back_populates="movimentacoes")
    usuario: Optional["Usuario"] = Relationship(back_populates="movimentacoes")
    pedido: Optional["Pedido"] = Relationship(back_populates="movimentacoes")

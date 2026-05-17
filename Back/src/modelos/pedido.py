from typing import TYPE_CHECKING, Any, ClassVar, Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship

from src.modelos.base import DatasMixin, IdMixin, StatusPedido

if TYPE_CHECKING:
    from src.modelos.autenticacao import Usuario
    from src.modelos.estoque import Deposito, Movimentacao, Produto


class Pedido(IdMixin, DatasMixin, table=True):
    @declared_attr.directive
    def __tablename__(cls: type[Any]) -> str:
        return "pedidos"

    deposito_id: UUID = Field(foreign_key="depositos.id", index=True)
    usuario_id: UUID | None = Field(default=None, foreign_key="usuarios.id", index=True)
    status: StatusPedido = Field(default=StatusPedido.ABERTO, index=True)
    observacao: str | None = Field(default=None, max_length=500)

    deposito: Optional["Deposito"] = Relationship(back_populates="pedidos")
    usuario: Optional["Usuario"] = Relationship(back_populates="pedidos")
    itens: list["ItemPedido"] = Relationship(back_populates="pedido")
    movimentacoes: list["Movimentacao"] = Relationship(back_populates="pedido")


class ItemPedido(IdMixin, DatasMixin, table=True):
    __table_args__: ClassVar[tuple[UniqueConstraint]] = (
        UniqueConstraint("deposito_id", "pedido_id", "produto_id", name="uq_itens_pedido_produto"),
    )

    @declared_attr.directive
    def __tablename__(cls: type[Any]) -> str:
        return "itens_pedido"

    deposito_id: UUID = Field(foreign_key="depositos.id", index=True)
    pedido_id: UUID = Field(foreign_key="pedidos.id", index=True)
    produto_id: UUID = Field(foreign_key="produtos.id", index=True)
    quantidade: int = Field(gt=0)

    deposito: Optional["Deposito"] = Relationship(back_populates="itens_pedido")
    pedido: Pedido | None = Relationship(back_populates="itens")
    produto: Optional["Produto"] = Relationship(back_populates="itens_pedido")

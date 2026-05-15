from typing import Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.modelos.base import DatasMixin, IdMixin, StatusPedido


class Pedido(IdMixin, DatasMixin, table=True):
    __tablename__ = "pedidos"

    usuario_id: UUID | None = Field(default=None, foreign_key="usuarios.id", index=True)
    status: StatusPedido = Field(default=StatusPedido.ABERTO, index=True)
    observacao: str | None = Field(default=None, max_length=500)

    usuario: Optional["Usuario"] = Relationship(back_populates="pedidos")
    itens: list["ItemPedido"] = Relationship(back_populates="pedido")
    movimentacoes: list["Movimentacao"] = Relationship(back_populates="pedido")


class ItemPedido(IdMixin, DatasMixin, table=True):
    __tablename__ = "itens_pedido"
    __table_args__ = (UniqueConstraint("pedido_id", "produto_id", name="uq_itens_pedido_produto"),)

    pedido_id: UUID = Field(foreign_key="pedidos.id", index=True)
    produto_id: UUID = Field(foreign_key="produtos.id", index=True)
    quantidade: int = Field(gt=0)

    pedido: Pedido | None = Relationship(back_populates="itens")
    produto: Optional["Produto"] = Relationship(back_populates="itens_pedido")

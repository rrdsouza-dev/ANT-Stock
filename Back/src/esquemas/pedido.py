from uuid import UUID

from pydantic import BaseModel, Field

from src.esquemas.base import SchemaComDatas
from src.modelos import StatusPedido


class PedidoEntrada(BaseModel):
    usuario_id: UUID | None = None
    status: StatusPedido = StatusPedido.ABERTO
    observacao: str | None = Field(default=None, max_length=500)


class PedidoAtualizar(BaseModel):
    usuario_id: UUID | None = None
    status: StatusPedido | None = None
    observacao: str | None = Field(default=None, max_length=500)


class PedidoSaida(PedidoEntrada, SchemaComDatas):
    pass


class ItemPedidoEntrada(BaseModel):
    produto_id: UUID
    quantidade: int = Field(gt=0)


class ItemPedidoSaida(ItemPedidoEntrada, SchemaComDatas):
    pedido_id: UUID

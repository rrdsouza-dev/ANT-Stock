from uuid import UUID

from sqlalchemy import select
from sqlmodel import col

from src.modelos import ItemPedido, Pedido
from src.repositorios.base import RepositorioSQL


class RepositorioPedido(RepositorioSQL[Pedido]):
    modelo = Pedido


class RepositorioItemPedido(RepositorioSQL[ItemPedido]):
    modelo = ItemPedido

    async def por_pedido(self, deposito_id: UUID, pedido_id: UUID) -> list[ItemPedido]:
        resultado = await self.sessao.execute(
            select(ItemPedido).where(
                col(ItemPedido.deposito_id) == deposito_id,
                col(ItemPedido.pedido_id) == pedido_id,
            )
        )
        return list(resultado.scalars().all())

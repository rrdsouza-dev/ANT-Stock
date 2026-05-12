from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Category, Location, Movement, Product, Stock
from src.repositories import (
    CategoryRepository,
    LocationRepository,
    MovementRepository,
    ProductRepository,
    StockRepository,
)
from src.services.crud import CRUDService


class InventoryServices:
    def __init__(self, session: AsyncSession) -> None:
        self.categories = CRUDService[Category](CategoryRepository(session), "Categoria")
        self.locations = CRUDService[Location](LocationRepository(session), "Localizacao")
        self.products = CRUDService[Product](ProductRepository(session), "Produto")
        self.stocks = CRUDService[Stock](StockRepository(session), "Estoque")
        self.movements = CRUDService[Movement](MovementRepository(session), "Movimentacao")

    async def estoque_do_produto(self, product_id: UUID) -> list[Stock]:
        return await self.stocks.listar(filters={"product_id": product_id})

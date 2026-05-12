# Repositorios dos recursos de estoque.
from src.models import Category, Location, Movement, Product, Stock
from src.repositories.base import SQLModelRepository


class CategoryRepository(SQLModelRepository[Category]):
    model = Category


class LocationRepository(SQLModelRepository[Location]):
    model = Location


class ProductRepository(SQLModelRepository[Product]):
    model = Product


class StockRepository(SQLModelRepository[Stock]):
    model = Stock


class MovementRepository(SQLModelRepository[Movement]):
    model = Movement

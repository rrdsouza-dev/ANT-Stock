# Agrega todos os roteadores da API.
from fastapi import APIRouter

from src.api.endpoints import auth, category, location, movement, product, stock

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(category.router)
api_router.include_router(location.router)
api_router.include_router(product.router)
api_router.include_router(stock.router)
api_router.include_router(movement.router)

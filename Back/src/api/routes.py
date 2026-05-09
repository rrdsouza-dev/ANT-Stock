from fastapi import APIRouter

from src.api.endpoints import auth, categories, locations, movements, products, stocks

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(locations.router)
api_router.include_router(products.router)
api_router.include_router(stocks.router)
api_router.include_router(movements.router)

# Exporta schemas usados nas entradas e respostas da API.
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead
from src.schemas.base import APIMessage
from src.schemas.stock import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    LocationCreate,
    LocationRead,
    LocationUpdate,
    MovementCreate,
    MovementOperationCreate,
    MovementRead,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    StockCreate,
    StockRead,
    StockUpdate,
)

__all__ = [
    "APIMessage",
    "CategoryCreate",
    "CategoryRead",
    "CategoryUpdate",
    "LocationCreate",
    "LocationRead",
    "LocationUpdate",
    "LoginRequest",
    "MovementCreate",
    "MovementOperationCreate",
    "MovementRead",
    "ProductCreate",
    "ProductRead",
    "ProductUpdate",
    "RegisterRequest",
    "StockCreate",
    "StockRead",
    "StockUpdate",
    "TokenResponse",
    "UserRead",
]

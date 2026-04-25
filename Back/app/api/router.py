from fastapi import APIRouter

from app.api.routes.categories import router as categories_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.locations import router as locations_router
from app.api.routes.movements import router as movements_router
from app.api.routes.products import router as products_router


# Agrupa todas as rotas expostas pela API.
api_router = APIRouter()

# Produtos sao o nucleo do controle de estoque.
api_router.include_router(products_router)

# Categorias ajudam na organizacao logica do armazem.
api_router.include_router(categories_router)

# Localizacoes representam onde os itens ficam armazenados.
api_router.include_router(locations_router)

# Estoque concentra consultas de disponibilidade.
api_router.include_router(inventory_router)

# Movimentacoes registram entradas e saidas de itens.
api_router.include_router(movements_router)

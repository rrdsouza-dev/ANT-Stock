from fastapi import APIRouter

from app.api.routes.autenticacao import router as autenticacao_router
from app.api.routes.categorias import router as categorias_router
from app.api.routes.estoque import router as estoque_router
from app.api.routes.localizacoes import router as localizacoes_router
from app.api.routes.movimentacoes import router as movimentacoes_router
from app.api.routes.produtos import router as produtos_router


api_router = APIRouter()

# Ponto unico onde os modulos da API sao conectados ao FastAPI.
api_router.include_router(autenticacao_router)
api_router.include_router(produtos_router)
api_router.include_router(categorias_router)
api_router.include_router(localizacoes_router)
api_router.include_router(estoque_router)
api_router.include_router(movimentacoes_router)

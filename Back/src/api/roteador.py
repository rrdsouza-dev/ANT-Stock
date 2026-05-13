from fastapi import APIRouter

from src.api.rotas import autenticacao, categorias, estoque, localizacoes, movimentacoes, pedidos, produtos

roteador_api = APIRouter()
roteador_api.include_router(autenticacao.router)
roteador_api.include_router(categorias.router)
roteador_api.include_router(localizacoes.router)
roteador_api.include_router(produtos.router)
roteador_api.include_router(estoque.router)
roteador_api.include_router(movimentacoes.router)
roteador_api.include_router(pedidos.router)

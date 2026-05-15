from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.roteador import roteador_api
from src.banco.sessao import engine
from src.intermediarios import id_requisicao
from src.nucleo.configuracao import configuracao
from src.nucleo.erros import (
    ErroApp,
    tratar_erro_app,
    tratar_erro_geral,
    tratar_erro_http,
    tratar_integridade,
    tratar_validacao,
)
from src.nucleo.logs import configurar_logs

config = configuracao()
configurar_logs(config)
ExceptionHandler = Any


@asynccontextmanager
async def ciclo_vida(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def criar_app() -> FastAPI:
    app = FastAPI(
        title=config.nome_app,
        description="Backend leve do sistema WMS ANT.",
        version=config.versao_app,
        debug=config.depurar,
        lifespan=ciclo_vida,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origem) for origem in config.origens_cors],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(id_requisicao)

    app.add_exception_handler(ErroApp, cast(ExceptionHandler, tratar_erro_app))
    app.add_exception_handler(StarletteHTTPException, cast(ExceptionHandler, tratar_erro_http))
    app.add_exception_handler(ValidationError, cast(ExceptionHandler, tratar_validacao))
    app.add_exception_handler(IntegrityError, cast(ExceptionHandler, tratar_integridade))
    app.add_exception_handler(Exception, cast(ExceptionHandler, tratar_erro_geral))

    app.include_router(roteador_api, prefix=config.prefixo_api)

    @app.get("/", tags=["Raiz"])
    async def raiz() -> dict[str, str]:
        return {"mensagem": "ANT API online", "versao": config.versao_app}

    @app.get("/health", tags=["Saude"])
    async def saude() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = criar_app()

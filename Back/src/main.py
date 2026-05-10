from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.routes import api_router
from src.core.config import config
from src.core.exceptions import (
    AppError,
    tratar_erro_app,
    tratar_erro_geral,
    tratar_erro_http,
    tratar_integridade,
    tratar_validacao,
)
from src.core.logging import configurar_logs
from src.database.session import engine
from src.middlewares import id_requisicao

settings = config()
configurar_logs(settings)
ExceptionHandler = Any


@asynccontextmanager
async def ciclo_vida(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def criar_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Backend moderno do ANT Stock.",
        version=settings.app_version,
        debug=settings.debug,
        lifespan=ciclo_vida,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(id_requisicao)

    app.add_exception_handler(AppError, cast(ExceptionHandler, tratar_erro_app))
    app.add_exception_handler(StarletteHTTPException, cast(ExceptionHandler, tratar_erro_http))
    app.add_exception_handler(ValidationError, cast(ExceptionHandler, tratar_validacao))
    app.add_exception_handler(IntegrityError, cast(ExceptionHandler, tratar_integridade))
    app.add_exception_handler(Exception, cast(ExceptionHandler, tratar_erro_geral))

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/", tags=["Raiz"])
    async def raiz() -> dict[str, str]:
        return {"message": "ANT Stock API online", "version": settings.app_version}

    @app.get("/health", tags=["Saude"])
    async def saude() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = criar_app()

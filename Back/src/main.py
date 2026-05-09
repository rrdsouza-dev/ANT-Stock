from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.routes import api_router
from src.core.config import get_settings
from src.core.exceptions import (
    AppError,
    app_error_handler,
    http_error_handler,
    integrity_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from src.core.logging import configure_logging
from src.database.session import engine
from src.middlewares import request_id_middleware

settings = get_settings()
configure_logging(settings)
ExceptionHandler = Any


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Backend moderno do ANT Stock.",
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_id_middleware)

    app.add_exception_handler(AppError, cast(ExceptionHandler, app_error_handler))
    app.add_exception_handler(StarletteHTTPException, cast(ExceptionHandler, http_error_handler))
    app.add_exception_handler(ValidationError, cast(ExceptionHandler, validation_error_handler))
    app.add_exception_handler(IntegrityError, cast(ExceptionHandler, integrity_error_handler))
    app.add_exception_handler(Exception, cast(ExceptionHandler, unhandled_error_handler))

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/", tags=["Raiz"])
    async def root() -> dict[str, str]:
        return {"message": "ANT Stock API online", "version": settings.app_version}

    @app.get("/health", tags=["Saude"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

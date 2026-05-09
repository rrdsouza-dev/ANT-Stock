from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "app_error",
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code


async def app_error_handler(_: Request, exc: AppError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


async def http_error_handler(_: Request, exc: StarletteHTTPException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


async def validation_error_handler(_: Request, exc: ValidationError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


async def integrity_error_handler(_: Request, exc: IntegrityError) -> ORJSONResponse:
    logger.warning("Database integrity error: {}", exc.orig)
    return ORJSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Registro duplicado ou relacionado a dados invalidos.", "code": "integrity_error"},
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> ORJSONResponse:
    logger.exception("Unhandled error at {}: {}", request.url.path, exc)
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor.", "code": "internal_server_error"},
    )

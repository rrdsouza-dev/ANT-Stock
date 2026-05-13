from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErroApp(Exception):
    def __init__(
        self,
        mensagem: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        codigo: str = "erro_app",
    ) -> None:
        self.mensagem = mensagem
        self.status_code = status_code
        self.codigo = codigo


async def tratar_erro_app(_: Request, exc: ErroApp) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detalhe": exc.mensagem, "codigo": exc.codigo},
    )


async def tratar_erro_http(_: Request, exc: StarletteHTTPException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detalhe": exc.detail},
        headers=getattr(exc, "headers", None),
    )


async def tratar_validacao(_: Request, exc: ValidationError) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detalhe": exc.errors()},
    )


async def tratar_integridade(_: Request, exc: IntegrityError) -> ORJSONResponse:
    logger.warning("Erro de integridade no banco: {}", exc.orig)
    return ORJSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detalhe": "Registro duplicado ou relacionado a dados invalidos.", "codigo": "erro_integridade"},
    )


async def tratar_erro_geral(request: Request, exc: Exception) -> ORJSONResponse:
    logger.exception("Erro inesperado em {}: {}", request.url.path, exc)
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detalhe": "Erro interno do servidor.", "codigo": "erro_interno"},
    )

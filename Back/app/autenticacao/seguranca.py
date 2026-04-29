from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import obter_config


def criar_token(dados: dict[str, Any], minutos: int | None = None) -> str:
    config = obter_config()
    carga = dados | {
        "exp": datetime.now(UTC) + timedelta(
            minutes=minutos or config.jwt_expira_minutos
        )
    }
    return jwt.encode(carga, config.jwt_chave, algorithm=config.jwt_algoritmo)


def ler_token(token: str) -> dict[str, Any]:
    config = obter_config()

    try:
        return jwt.decode(token, config.jwt_chave, algorithms=[config.jwt_algoritmo])
    except JWTError as exc:
        raise ValueError("Token JWT invalido.") from exc

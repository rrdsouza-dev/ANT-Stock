# Funcoes de senha e tokens JWT.
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from src.core.config import config

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash(password: str) -> str:
    return cast(str, password_context.hash(password))


def checar_senha(password: str, password_hash: str) -> bool:
    return cast(bool, password_context.verify(password, password_hash))


def criar_token(subject: str, claims: dict[str, Any] | None = None) -> str:
    settings = config()
    now = datetime.now(UTC)
    # O JWT precisa manter "sub" e "exp" para a validacao feita no login autenticado.
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
        "iss": "ant-stock",
    }
    if claims:
        payload.update(claims)
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def ler_token(token: str) -> dict[str, Any]:
    settings = config()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
    except InvalidTokenError as exc:
        raise ValueError("Token JWT invalido.") from exc

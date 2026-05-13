from datetime import UTC, datetime, timedelta
from typing import Any, cast

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

from src.nucleo.configuracao import configuracao

contexto_senha = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash(senha: str) -> str:
    return cast(str, contexto_senha.hash(senha))


def checar_senha(senha: str, senha_hash: str) -> bool:
    return cast(bool, contexto_senha.verify(senha, senha_hash))


def criar_token(usuario_id: str, dados: dict[str, Any] | None = None) -> str:
    config = configuracao()
    agora = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": usuario_id,
        "iat": agora,
        "exp": agora + timedelta(minutes=config.jwt_expira_minutos),
        "iss": "ant",
    }
    if dados:
        payload.update(dados)
    return jwt.encode(payload, config.jwt_chave.get_secret_value(), algorithm=config.jwt_algoritmo)


def ler_token(token: str) -> dict[str, Any]:
    config = configuracao()
    try:
        return jwt.decode(
            token,
            config.jwt_chave.get_secret_value(),
            algorithms=[config.jwt_algoritmo],
            options={"require": ["exp", "sub"]},
        )
    except InvalidTokenError as exc:
        raise ValueError("Token JWT invalido.") from exc

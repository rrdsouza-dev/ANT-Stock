from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings


# Mantem o mecanismo de hash pronto para futuras senhas locais.
hash_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    return hash_ctx.hash(senha)


def confere_senha(senha: str, senha_hash: str) -> bool:
    return hash_ctx.verify(senha, senha_hash)


def criar_token(dados: dict[str, Any], minutos: int | None = None) -> str:
    # Gera um JWT curto para fluxos internos, como estado do Google ou token auxiliar.
    config = get_settings()
    carga = dados.copy()
    carga["exp"] = datetime.now(UTC) + timedelta(
        minutes=minutos or config.jwt_expira_minutos
    )
    return jwt.encode(carga, config.jwt_chave, algorithm=config.jwt_algoritmo)


def ler_token(token: str) -> dict[str, Any]:
    config = get_settings()

    try:
        return jwt.decode(
            token,
            config.jwt_chave,
            algorithms=[config.jwt_algoritmo],
        )
    except JWTError as exc:
        raise ValueError("Token JWT invalido.") from exc

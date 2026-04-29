from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.autenticacao.contas import buscar_perfil
from app.models.comum.usuario import Usuario


bearer = HTTPBearer(auto_error=False)


def token_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> str:
    if not credenciais or credenciais.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer obrigatorio.",
        )

    return credenciais.credentials


def usuario_atual(token: str = Depends(token_atual)) -> Usuario:
    return buscar_perfil(token)

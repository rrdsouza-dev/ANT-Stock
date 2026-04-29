from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.servico import perfil
from app.models.usuario import Usuario


bearer = HTTPBearer(auto_error=False)


def token_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> str:
    # Extrai o token Bearer usado nas rotas protegidas.
    if not credenciais or credenciais.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer obrigatorio.",
        )

    return credenciais.credentials


def usuario_atual(token: str = Depends(token_atual)) -> Usuario:
    # Resolve o usuario autenticado a partir do token enviado.
    return perfil(token)

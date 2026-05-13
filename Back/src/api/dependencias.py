from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.banco.sessao import abrir_sessao
from src.modelos import Usuario
from src.nucleo.seguranca import ler_token
from src.repositorios.autenticacao import RepositorioUsuario

bearer = HTTPBearer(auto_error=False)


async def sessao_db() -> AsyncGenerator[AsyncSession, None]:
    async for sessao in abrir_sessao():
        yield sessao


async def usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(bearer),
    sessao: AsyncSession = Depends(sessao_db),
) -> Usuario:
    if credenciais is None or credenciais.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Bearer obrigatorio.")

    try:
        payload = ler_token(credenciais.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.") from exc

    usuario_id = payload.get("sub")
    if not usuario_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")

    usuario = await RepositorioUsuario(sessao).buscar(usuario_id)
    if usuario is None or not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao autenticado.")
    return usuario

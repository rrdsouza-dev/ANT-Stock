from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.banco.sessao import abrir_sessao
from src.modelos import Usuario
from src.nucleo.erros import ErroApp
from src.nucleo.seguranca import ler_token
from src.repositorios.autenticacao import RepositorioUsuario
from src.servicos.autenticacao import ServicoAutenticacao

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

    try:
        usuario_uuid = UUID(str(usuario_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.") from exc

    usuario = await RepositorioUsuario(sessao).buscar(usuario_uuid)
    if usuario is None or not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao autenticado.")
    return usuario


async def verificar_acesso_deposito(
    deposito_id: UUID = Path(...),
    usuario: Usuario = Depends(usuario_atual),
    sessao: AsyncSession = Depends(sessao_db),
) -> tuple[Usuario, UUID]:
    tem_acesso = await ServicoAutenticacao(sessao).verificar_acesso(usuario.id, deposito_id)
    if not tem_acesso:
        raise ErroApp("Sem acesso a este deposito", status_code=403, codigo="sem_acesso_deposito")
    return usuario, deposito_id

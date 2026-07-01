from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import exigir_perfis, sessao_db
from src.esquemas import UsuarioSaida
from src.modelos import PerfilCodigo, Usuario
from src.servicos import ServicoAutenticacao

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("", response_model=list[UsuarioSaida])
async def listar(
    _: Usuario = Depends(exigir_perfis(PerfilCodigo.GESTAO)),
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
) -> list[UsuarioSaida]:
    usuarios = await ServicoAutenticacao(sessao).listar_usuarios(inicio=inicio, limite=limite)
    return [UsuarioSaida.de_modelo(usuario) for usuario in usuarios]

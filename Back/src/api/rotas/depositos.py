from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db, usuario_atual
from src.esquemas import DepositoSaida
from src.modelos import PerfilCodigo, Usuario
from src.repositorios import RepositorioDeposito

router = APIRouter(prefix="/depositos", tags=["Depositos"])


@router.get("", response_model=list[DepositoSaida])
async def listar(
    usuario: Usuario = Depends(usuario_atual),
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
) -> list[DepositoSaida]:
    repositorio = RepositorioDeposito(sessao)
    if usuario.perfil and usuario.perfil.codigo == PerfilCodigo.GESTAO:
        depositos = await repositorio.listar(inicio=inicio, limite=limite, filtros={"ativo": True})
    else:
        depositos = await repositorio.por_usuario(usuario.id, inicio=inicio, limite=limite)
    return [DepositoSaida.model_validate(deposito) for deposito in depositos]

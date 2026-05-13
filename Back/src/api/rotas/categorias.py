from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db
from src.esquemas import CategoriaAtualizar, CategoriaEntrada, CategoriaSaida, MensagemAPI
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("", response_model=list[CategoriaSaida])
async def listar(
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
) -> list[CategoriaSaida]:
    itens = await ServicoEstoque(sessao).categorias.listar(inicio=inicio, limite=limite)
    return [CategoriaSaida.model_validate(item) for item in itens]


@router.get("/{categoria_id}", response_model=CategoriaSaida)
async def buscar(categoria_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> CategoriaSaida:
    return CategoriaSaida.model_validate(await ServicoEstoque(sessao).categorias.buscar(categoria_id))


@router.post("", response_model=CategoriaSaida, status_code=status.HTTP_201_CREATED)
async def criar(dados: CategoriaEntrada, sessao: AsyncSession = Depends(sessao_db)) -> CategoriaSaida:
    item = await ServicoEstoque(sessao).categorias.criar(dados.model_dump())
    return CategoriaSaida.model_validate(item)


@router.patch("/{categoria_id}", response_model=CategoriaSaida)
async def editar(
    categoria_id: UUID,
    dados: CategoriaAtualizar,
    sessao: AsyncSession = Depends(sessao_db),
) -> CategoriaSaida:
    item = await ServicoEstoque(sessao).categorias.editar(categoria_id, dados.model_dump(exclude_unset=True))
    return CategoriaSaida.model_validate(item)


@router.delete("/{categoria_id}", response_model=MensagemAPI)
async def remover(categoria_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> MensagemAPI:
    await ServicoEstoque(sessao).categorias.remover(categoria_id)
    return MensagemAPI(mensagem="Categoria removida.")

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db
from src.esquemas import MensagemAPI, ProdutoAtualizar, ProdutoEntrada, ProdutoSaida
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("", response_model=list[ProdutoSaida])
async def listar(
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
) -> list[ProdutoSaida]:
    itens = await ServicoEstoque(sessao).produtos.listar(inicio=inicio, limite=limite)
    return [ProdutoSaida.model_validate(item) for item in itens]


@router.get("/{produto_id}", response_model=ProdutoSaida)
async def buscar(produto_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> ProdutoSaida:
    return ProdutoSaida.model_validate(await ServicoEstoque(sessao).produtos.buscar(produto_id))


@router.post("", response_model=ProdutoSaida, status_code=status.HTTP_201_CREATED)
async def criar(dados: ProdutoEntrada, sessao: AsyncSession = Depends(sessao_db)) -> ProdutoSaida:
    item = await ServicoEstoque(sessao).produtos.criar(dados.model_dump())
    return ProdutoSaida.model_validate(item)


@router.patch("/{produto_id}", response_model=ProdutoSaida)
async def editar(
    produto_id: UUID,
    dados: ProdutoAtualizar,
    sessao: AsyncSession = Depends(sessao_db),
) -> ProdutoSaida:
    item = await ServicoEstoque(sessao).produtos.editar(produto_id, dados.model_dump(exclude_unset=True))
    return ProdutoSaida.model_validate(item)


@router.delete("/{produto_id}", response_model=MensagemAPI)
async def remover(produto_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> MensagemAPI:
    await ServicoEstoque(sessao).produtos.remover(produto_id)
    return MensagemAPI(mensagem="Produto removido.")

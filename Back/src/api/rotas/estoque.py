from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db
from src.esquemas import EstoqueAtualizar, EstoqueEntrada, EstoqueSaida, MensagemAPI
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("", response_model=list[EstoqueSaida])
async def listar(
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
    localizacao_id: UUID | None = Query(default=None),
) -> list[EstoqueSaida]:
    itens = await ServicoEstoque(sessao).estoque.listar(
        inicio=inicio,
        limite=limite,
        filtros={"localizacao_id": localizacao_id},
    )
    return [EstoqueSaida.model_validate(item) for item in itens]


@router.get("/produto/{produto_id}", response_model=list[EstoqueSaida])
async def por_produto(produto_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> list[EstoqueSaida]:
    itens = await ServicoEstoque(sessao).estoque_do_produto(produto_id)
    return [EstoqueSaida.model_validate(item) for item in itens]


@router.post("", response_model=EstoqueSaida, status_code=status.HTTP_201_CREATED)
async def criar(dados: EstoqueEntrada, sessao: AsyncSession = Depends(sessao_db)) -> EstoqueSaida:
    item = await ServicoEstoque(sessao).estoque.criar(dados.model_dump())
    return EstoqueSaida.model_validate(item)


@router.patch("/{estoque_id}", response_model=EstoqueSaida)
async def editar(
    estoque_id: UUID,
    dados: EstoqueAtualizar,
    sessao: AsyncSession = Depends(sessao_db),
) -> EstoqueSaida:
    item = await ServicoEstoque(sessao).estoque.editar(estoque_id, dados.model_dump(exclude_unset=True))
    return EstoqueSaida.model_validate(item)


@router.delete("/{estoque_id}", response_model=MensagemAPI)
async def remover(estoque_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> MensagemAPI:
    await ServicoEstoque(sessao).estoque.remover(estoque_id)
    return MensagemAPI(mensagem="Estoque removido.")

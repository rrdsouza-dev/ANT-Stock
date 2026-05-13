from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db
from src.esquemas import MovimentacaoEntrada, MovimentacaoOperacaoEntrada, MovimentacaoSaida
from src.modelos import TipoMovimentacao
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/movimentacoes", tags=["Movimentacoes"])


@router.get("", response_model=list[MovimentacaoSaida])
async def listar(
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
    produto_id: UUID | None = Query(default=None),
    pedido_id: UUID | None = Query(default=None),
) -> list[MovimentacaoSaida]:
    itens = await ServicoEstoque(sessao).movimentacoes.listar(
        inicio=inicio,
        limite=limite,
        filtros={"produto_id": produto_id, "pedido_id": pedido_id},
    )
    return [MovimentacaoSaida.model_validate(item) for item in itens]


@router.get("/{movimentacao_id}", response_model=MovimentacaoSaida)
async def buscar(movimentacao_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> MovimentacaoSaida:
    return MovimentacaoSaida.model_validate(await ServicoEstoque(sessao).movimentacoes.buscar(movimentacao_id))


@router.post("", response_model=MovimentacaoSaida, status_code=status.HTTP_201_CREATED)
async def criar(dados: MovimentacaoEntrada, sessao: AsyncSession = Depends(sessao_db)) -> MovimentacaoSaida:
    item = await ServicoEstoque(sessao).registrar_movimentacao(dados.model_dump())
    return MovimentacaoSaida.model_validate(item)


@router.post("/entrada", response_model=MovimentacaoSaida, status_code=status.HTTP_201_CREATED)
async def entrada(
    dados: MovimentacaoOperacaoEntrada,
    sessao: AsyncSession = Depends(sessao_db),
) -> MovimentacaoSaida:
    payload = dados.model_dump()
    payload["tipo"] = TipoMovimentacao.ENTRADA
    item = await ServicoEstoque(sessao).registrar_movimentacao(payload)
    return MovimentacaoSaida.model_validate(item)


@router.post("/saida", response_model=MovimentacaoSaida, status_code=status.HTTP_201_CREATED)
async def saida(
    dados: MovimentacaoOperacaoEntrada,
    sessao: AsyncSession = Depends(sessao_db),
) -> MovimentacaoSaida:
    payload = dados.model_dump()
    payload["tipo"] = TipoMovimentacao.SAIDA
    item = await ServicoEstoque(sessao).registrar_movimentacao(payload)
    return MovimentacaoSaida.model_validate(item)

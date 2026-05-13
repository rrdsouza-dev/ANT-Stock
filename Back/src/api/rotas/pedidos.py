from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db
from src.esquemas import (
    ItemPedidoEntrada,
    ItemPedidoSaida,
    MensagemAPI,
    PedidoAtualizar,
    PedidoEntrada,
    PedidoSaida,
)
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("", response_model=list[PedidoSaida])
async def listar(
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
    usuario_id: UUID | None = Query(default=None),
) -> list[PedidoSaida]:
    itens = await ServicoEstoque(sessao).pedidos.listar(
        inicio=inicio,
        limite=limite,
        filtros={"usuario_id": usuario_id},
    )
    return [PedidoSaida.model_validate(item) for item in itens]


@router.get("/{pedido_id}", response_model=PedidoSaida)
async def buscar(pedido_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> PedidoSaida:
    return PedidoSaida.model_validate(await ServicoEstoque(sessao).pedidos.buscar(pedido_id))


@router.post("", response_model=PedidoSaida, status_code=status.HTTP_201_CREATED)
async def criar(dados: PedidoEntrada, sessao: AsyncSession = Depends(sessao_db)) -> PedidoSaida:
    item = await ServicoEstoque(sessao).pedidos.criar(dados.model_dump())
    return PedidoSaida.model_validate(item)


@router.patch("/{pedido_id}", response_model=PedidoSaida)
async def editar(
    pedido_id: UUID,
    dados: PedidoAtualizar,
    sessao: AsyncSession = Depends(sessao_db),
) -> PedidoSaida:
    item = await ServicoEstoque(sessao).pedidos.editar(pedido_id, dados.model_dump(exclude_unset=True))
    return PedidoSaida.model_validate(item)


@router.delete("/{pedido_id}", response_model=MensagemAPI)
async def remover(pedido_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> MensagemAPI:
    await ServicoEstoque(sessao).pedidos.remover(pedido_id)
    return MensagemAPI(mensagem="Pedido removido.")


@router.get("/{pedido_id}/itens", response_model=list[ItemPedidoSaida])
async def listar_itens(pedido_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> list[ItemPedidoSaida]:
    itens = await ServicoEstoque(sessao).itens_do_pedido(pedido_id)
    return [ItemPedidoSaida.model_validate(item) for item in itens]


@router.post("/{pedido_id}/itens", response_model=ItemPedidoSaida, status_code=status.HTTP_201_CREATED)
async def adicionar_item(
    pedido_id: UUID,
    dados: ItemPedidoEntrada,
    sessao: AsyncSession = Depends(sessao_db),
) -> ItemPedidoSaida:
    payload = dados.model_dump()
    payload["pedido_id"] = pedido_id
    item = await ServicoEstoque(sessao).itens_pedido.criar(payload)
    return ItemPedidoSaida.model_validate(item)

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db, verificar_acesso_deposito
from src.esquemas import (
    ItemPedidoEntrada,
    ItemPedidoSaida,
    MensagemAPI,
    PedidoAtualizar,
    PedidoEntrada,
    PedidoSaida,
)
from src.modelos import Usuario
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/{deposito_id}/pedidos", tags=["Pedidos"])


@router.get("", response_model=list[PedidoSaida])
async def listar(
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
    usuario_id: UUID | None = Query(default=None),
) -> list[PedidoSaida]:
    usuario, deposito_id = usuario_deposito
    itens = await ServicoEstoque(sessao).listar_pedidos(
        usuario.id,
        deposito_id,
        inicio=inicio,
        limite=limite,
        usuario_filtro_id=usuario_id,
    )
    return [PedidoSaida.model_validate(item) for item in itens]


@router.get("/{pedido_id}", response_model=PedidoSaida)
async def buscar(
    pedido_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> PedidoSaida:
    usuario, deposito_id = usuario_deposito
    return PedidoSaida.model_validate(await ServicoEstoque(sessao).buscar_pedido(usuario.id, deposito_id, pedido_id))


@router.post("", response_model=PedidoSaida, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: PedidoEntrada,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> PedidoSaida:
    usuario, deposito_id = usuario_deposito
    payload = dados.model_dump()
    payload["usuario_id"] = payload.get("usuario_id") or usuario.id
    item = await ServicoEstoque(sessao).criar_pedido(usuario.id, deposito_id, payload)
    return PedidoSaida.model_validate(item)


@router.patch("/{pedido_id}", response_model=PedidoSaida)
async def editar(
    pedido_id: UUID,
    dados: PedidoAtualizar,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> PedidoSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).editar_pedido(
        usuario.id,
        deposito_id,
        pedido_id,
        dados.model_dump(exclude_unset=True),
    )
    return PedidoSaida.model_validate(item)


@router.delete("/{pedido_id}", response_model=MensagemAPI)
async def remover(
    pedido_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> MensagemAPI:
    usuario, deposito_id = usuario_deposito
    await ServicoEstoque(sessao).remover_pedido(usuario.id, deposito_id, pedido_id)
    return MensagemAPI(mensagem="Pedido removido.")


@router.get("/{pedido_id}/itens", response_model=list[ItemPedidoSaida])
async def listar_itens(
    pedido_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> list[ItemPedidoSaida]:
    usuario, deposito_id = usuario_deposito
    itens = await ServicoEstoque(sessao).itens_do_pedido(usuario.id, deposito_id, pedido_id)
    return [ItemPedidoSaida.model_validate(item) for item in itens]


@router.post("/{pedido_id}/itens", response_model=ItemPedidoSaida, status_code=status.HTTP_201_CREATED)
async def adicionar_item(
    pedido_id: UUID,
    dados: ItemPedidoEntrada,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> ItemPedidoSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).adicionar_item_pedido(usuario.id, deposito_id, pedido_id, dados.model_dump())
    return ItemPedidoSaida.model_validate(item)

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db, verificar_acesso_deposito
from src.esquemas import MovimentacaoEntrada, MovimentacaoOperacaoEntrada, MovimentacaoSaida
from src.modelos import TipoMovimentacao, Usuario
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/{deposito_id}/movimentacoes", tags=["Movimentacoes"])


@router.get("", response_model=list[MovimentacaoSaida])
async def listar(
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
    produto_id: UUID | None = Query(default=None),
    pedido_id: UUID | None = Query(default=None),
) -> list[MovimentacaoSaida]:
    usuario, deposito_id = usuario_deposito
    itens = await ServicoEstoque(sessao).listar_movimentacoes(
        usuario.id,
        deposito_id,
        inicio=inicio,
        limite=limite,
        produto_id=produto_id,
        pedido_id=pedido_id,
    )
    return [MovimentacaoSaida.model_validate(item) for item in itens]


@router.get("/{movimentacao_id}", response_model=MovimentacaoSaida)
async def buscar(
    movimentacao_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> MovimentacaoSaida:
    usuario, deposito_id = usuario_deposito
    return MovimentacaoSaida.model_validate(
        await ServicoEstoque(sessao).buscar_movimentacao(usuario.id, deposito_id, movimentacao_id)
    )


@router.post("", response_model=MovimentacaoSaida, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: MovimentacaoEntrada,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> MovimentacaoSaida:
    usuario, deposito_id = usuario_deposito
    payload = dados.model_dump()
    payload["usuario_id"] = payload.get("usuario_id") or usuario.id
    item = await ServicoEstoque(sessao).registrar_movimentacao(usuario.id, deposito_id, payload)
    return MovimentacaoSaida.model_validate(item)


@router.post("/entrada", response_model=MovimentacaoSaida, status_code=status.HTTP_201_CREATED)
async def entrada(
    dados: MovimentacaoOperacaoEntrada,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> MovimentacaoSaida:
    usuario, deposito_id = usuario_deposito
    payload = dados.model_dump()
    payload["usuario_id"] = payload.get("usuario_id") or usuario.id
    payload["tipo"] = TipoMovimentacao.ENTRADA
    item = await ServicoEstoque(sessao).registrar_movimentacao(usuario.id, deposito_id, payload)
    return MovimentacaoSaida.model_validate(item)


@router.post("/saida", response_model=MovimentacaoSaida, status_code=status.HTTP_201_CREATED)
async def saida(
    dados: MovimentacaoOperacaoEntrada,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> MovimentacaoSaida:
    usuario, deposito_id = usuario_deposito
    payload = dados.model_dump()
    payload["usuario_id"] = payload.get("usuario_id") or usuario.id
    payload["tipo"] = TipoMovimentacao.SAIDA
    item = await ServicoEstoque(sessao).registrar_movimentacao(usuario.id, deposito_id, payload)
    return MovimentacaoSaida.model_validate(item)

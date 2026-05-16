from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db, verificar_acesso_deposito
from src.esquemas import EstoqueAtualizar, EstoqueEntrada, EstoqueSaida, MensagemAPI
from src.modelos import Usuario
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/{deposito_id}/estoque", tags=["Estoque"])


@router.get("", response_model=list[EstoqueSaida])
async def listar(
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
    localizacao_id: UUID | None = Query(default=None),
) -> list[EstoqueSaida]:
    usuario, deposito_id = usuario_deposito
    itens = await ServicoEstoque(sessao).listar_estoque(
        usuario.id,
        deposito_id,
        inicio=inicio,
        limite=limite,
        localizacao_id=localizacao_id,
    )
    return [EstoqueSaida.model_validate(item) for item in itens]


@router.get("/produto/{produto_id}", response_model=list[EstoqueSaida])
async def por_produto(
    produto_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> list[EstoqueSaida]:
    usuario, deposito_id = usuario_deposito
    itens = await ServicoEstoque(sessao).estoque_do_produto(usuario.id, deposito_id, produto_id)
    return [EstoqueSaida.model_validate(item) for item in itens]


@router.post("", response_model=EstoqueSaida, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: EstoqueEntrada,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> EstoqueSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).criar_estoque(usuario.id, deposito_id, dados.model_dump())
    return EstoqueSaida.model_validate(item)


@router.patch("/{estoque_id}", response_model=EstoqueSaida)
async def editar(
    estoque_id: UUID,
    dados: EstoqueAtualizar,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> EstoqueSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).editar_estoque(
        usuario.id,
        deposito_id,
        estoque_id,
        dados.model_dump(exclude_unset=True),
    )
    return EstoqueSaida.model_validate(item)


@router.delete("/{estoque_id}", response_model=MensagemAPI)
async def remover(
    estoque_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> MensagemAPI:
    usuario, deposito_id = usuario_deposito
    await ServicoEstoque(sessao).remover_estoque(usuario.id, deposito_id, estoque_id)
    return MensagemAPI(mensagem="Estoque removido.")

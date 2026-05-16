from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db, verificar_acesso_deposito
from src.esquemas import MensagemAPI, ProdutoAtualizar, ProdutoEntrada, ProdutoSaida
from src.modelos import Usuario
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/{deposito_id}/produtos", tags=["Produtos"])


@router.get("", response_model=list[ProdutoSaida])
async def listar(
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
) -> list[ProdutoSaida]:
    usuario, deposito_id = usuario_deposito
    itens = await ServicoEstoque(sessao).listar_produtos(usuario.id, deposito_id, inicio=inicio, limite=limite)
    return [ProdutoSaida.model_validate(item) for item in itens]


@router.get("/{produto_id}", response_model=ProdutoSaida)
async def buscar(
    produto_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> ProdutoSaida:
    usuario, deposito_id = usuario_deposito
    return ProdutoSaida.model_validate(await ServicoEstoque(sessao).buscar_produto(usuario.id, deposito_id, produto_id))


@router.post("", response_model=ProdutoSaida, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: ProdutoEntrada,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> ProdutoSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).criar_produto(usuario.id, deposito_id, dados.model_dump())
    return ProdutoSaida.model_validate(item)


@router.patch("/{produto_id}", response_model=ProdutoSaida)
async def editar(
    produto_id: UUID,
    dados: ProdutoAtualizar,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> ProdutoSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).editar_produto(
        usuario.id,
        deposito_id,
        produto_id,
        dados.model_dump(exclude_unset=True),
    )
    return ProdutoSaida.model_validate(item)


@router.delete("/{produto_id}", response_model=MensagemAPI)
async def remover(
    produto_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> MensagemAPI:
    usuario, deposito_id = usuario_deposito
    await ServicoEstoque(sessao).remover_produto(usuario.id, deposito_id, produto_id)
    return MensagemAPI(mensagem="Produto removido.")

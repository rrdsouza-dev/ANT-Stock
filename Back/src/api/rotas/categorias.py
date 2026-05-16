from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db, verificar_acesso_deposito
from src.esquemas import CategoriaAtualizar, CategoriaEntrada, CategoriaSaida, MensagemAPI
from src.modelos import Usuario
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/{deposito_id}/categorias", tags=["Categorias"])


@router.get("", response_model=list[CategoriaSaida])
async def listar(
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
) -> list[CategoriaSaida]:
    usuario, deposito_id = usuario_deposito
    itens = await ServicoEstoque(sessao).listar_categorias(usuario.id, deposito_id, inicio=inicio, limite=limite)
    return [CategoriaSaida.model_validate(item) for item in itens]


@router.get("/{categoria_id}", response_model=CategoriaSaida)
async def buscar(
    categoria_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> CategoriaSaida:
    usuario, deposito_id = usuario_deposito
    return CategoriaSaida.model_validate(
        await ServicoEstoque(sessao).buscar_categoria(usuario.id, deposito_id, categoria_id)
    )


@router.post("", response_model=CategoriaSaida, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: CategoriaEntrada,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> CategoriaSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).criar_categoria(usuario.id, deposito_id, dados.model_dump())
    return CategoriaSaida.model_validate(item)


@router.patch("/{categoria_id}", response_model=CategoriaSaida)
async def editar(
    categoria_id: UUID,
    dados: CategoriaAtualizar,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> CategoriaSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).editar_categoria(
        usuario.id,
        deposito_id,
        categoria_id,
        dados.model_dump(exclude_unset=True),
    )
    return CategoriaSaida.model_validate(item)


@router.delete("/{categoria_id}", response_model=MensagemAPI)
async def remover(
    categoria_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> MensagemAPI:
    usuario, deposito_id = usuario_deposito
    await ServicoEstoque(sessao).remover_categoria(usuario.id, deposito_id, categoria_id)
    return MensagemAPI(mensagem="Categoria removida.")

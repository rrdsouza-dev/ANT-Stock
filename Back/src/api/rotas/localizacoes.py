from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db, verificar_acesso_deposito
from src.esquemas import LocalizacaoAtualizar, LocalizacaoEntrada, LocalizacaoSaida, MensagemAPI
from src.modelos import Usuario
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/{deposito_id}/localizacoes", tags=["Localizacoes"])


@router.get("", response_model=list[LocalizacaoSaida])
async def listar(
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
) -> list[LocalizacaoSaida]:
    usuario, deposito_id = usuario_deposito
    itens = await ServicoEstoque(sessao).listar_localizacoes(usuario.id, deposito_id, inicio=inicio, limite=limite)
    return [LocalizacaoSaida.model_validate(item) for item in itens]


@router.get("/{localizacao_id}", response_model=LocalizacaoSaida)
async def buscar(
    localizacao_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> LocalizacaoSaida:
    usuario, deposito_id = usuario_deposito
    return LocalizacaoSaida.model_validate(
        await ServicoEstoque(sessao).buscar_localizacao(usuario.id, deposito_id, localizacao_id)
    )


@router.post("", response_model=LocalizacaoSaida, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: LocalizacaoEntrada,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> LocalizacaoSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).criar_localizacao(usuario.id, deposito_id, dados.model_dump())
    return LocalizacaoSaida.model_validate(item)


@router.patch("/{localizacao_id}", response_model=LocalizacaoSaida)
async def editar(
    localizacao_id: UUID,
    dados: LocalizacaoAtualizar,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> LocalizacaoSaida:
    usuario, deposito_id = usuario_deposito
    item = await ServicoEstoque(sessao).editar_localizacao(
        usuario.id,
        deposito_id,
        localizacao_id,
        dados.model_dump(exclude_unset=True),
    )
    return LocalizacaoSaida.model_validate(item)


@router.delete("/{localizacao_id}", response_model=MensagemAPI)
async def remover(
    localizacao_id: UUID,
    usuario_deposito: tuple[Usuario, UUID] = Depends(verificar_acesso_deposito),
    sessao: AsyncSession = Depends(sessao_db),
) -> MensagemAPI:
    usuario, deposito_id = usuario_deposito
    await ServicoEstoque(sessao).remover_localizacao(usuario.id, deposito_id, localizacao_id)
    return MensagemAPI(mensagem="Localizacao removida.")

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db
from src.esquemas import LocalizacaoAtualizar, LocalizacaoEntrada, LocalizacaoSaida, MensagemAPI
from src.servicos import ServicoEstoque

router = APIRouter(prefix="/localizacoes", tags=["Localizacoes"])


@router.get("", response_model=list[LocalizacaoSaida])
async def listar(
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
) -> list[LocalizacaoSaida]:
    itens = await ServicoEstoque(sessao).localizacoes.listar(inicio=inicio, limite=limite)
    return [LocalizacaoSaida.model_validate(item) for item in itens]


@router.get("/{localizacao_id}", response_model=LocalizacaoSaida)
async def buscar(localizacao_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> LocalizacaoSaida:
    return LocalizacaoSaida.model_validate(await ServicoEstoque(sessao).localizacoes.buscar(localizacao_id))


@router.post("", response_model=LocalizacaoSaida, status_code=status.HTTP_201_CREATED)
async def criar(dados: LocalizacaoEntrada, sessao: AsyncSession = Depends(sessao_db)) -> LocalizacaoSaida:
    item = await ServicoEstoque(sessao).localizacoes.criar(dados.model_dump())
    return LocalizacaoSaida.model_validate(item)


@router.patch("/{localizacao_id}", response_model=LocalizacaoSaida)
async def editar(
    localizacao_id: UUID,
    dados: LocalizacaoAtualizar,
    sessao: AsyncSession = Depends(sessao_db),
) -> LocalizacaoSaida:
    item = await ServicoEstoque(sessao).localizacoes.editar(localizacao_id, dados.model_dump(exclude_unset=True))
    return LocalizacaoSaida.model_validate(item)


@router.delete("/{localizacao_id}", response_model=MensagemAPI)
async def remover(localizacao_id: UUID, sessao: AsyncSession = Depends(sessao_db)) -> MensagemAPI:
    await ServicoEstoque(sessao).localizacoes.remover(localizacao_id)
    return MensagemAPI(mensagem="Localizacao removida.")

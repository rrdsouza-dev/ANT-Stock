from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import exigir_perfis, sessao_db, usuario_atual
from src.esquemas import DepositoAtualizar, DepositoEntrada, DepositoSaida, MensagemAPI
from src.modelos import PerfilCodigo, Usuario
from src.nucleo.erros import ErroApp
from src.repositorios import RepositorioDeposito, RepositorioUsuarioDeposito

router = APIRouter(prefix="/depositos", tags=["Depositos"])


@router.get("", response_model=list[DepositoSaida])
async def listar(
    usuario: Usuario = Depends(usuario_atual),
    sessao: AsyncSession = Depends(sessao_db),
    inicio: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=1, le=200),
) -> list[DepositoSaida]:
    repositorio = RepositorioDeposito(sessao)
    if usuario.perfil and usuario.perfil.codigo == PerfilCodigo.GESTAO:
        depositos = await repositorio.listar(inicio=inicio, limite=limite, filtros={"ativo": True})
    else:
        depositos = await repositorio.por_usuario(usuario.id, inicio=inicio, limite=limite)
    return [DepositoSaida.model_validate(deposito) for deposito in depositos]


@router.post("", response_model=DepositoSaida, status_code=status.HTTP_201_CREATED)
async def criar(
    dados: DepositoEntrada,
    usuario: Usuario = Depends(exigir_perfis(PerfilCodigo.GESTAO)),
    sessao: AsyncSession = Depends(sessao_db),
) -> DepositoSaida:
    deposito = await RepositorioDeposito(sessao).criar(dados.model_dump())
    # Todos os usuarios ativos ja recebem acesso automatico ao deposito recem-criado,
    # mantendo o mesmo comportamento aplicado no cadastro de novos usuarios.
    await RepositorioUsuarioDeposito(sessao).vincular_todos_usuarios(deposito.id)
    return DepositoSaida.model_validate(deposito)


@router.patch("/{deposito_id}", response_model=DepositoSaida)
async def editar(
    deposito_id: UUID,
    dados: DepositoAtualizar,
    usuario: Usuario = Depends(exigir_perfis(PerfilCodigo.GESTAO)),
    sessao: AsyncSession = Depends(sessao_db),
) -> DepositoSaida:
    repositorio = RepositorioDeposito(sessao)
    deposito = await repositorio.buscar(deposito_id)
    if deposito is None:
        raise ErroApp("Deposito nao encontrado.", status_code=404, codigo="nao_encontrado")
    deposito = await repositorio.editar(deposito, dados.model_dump(exclude_unset=True))
    return DepositoSaida.model_validate(deposito)


@router.delete("/{deposito_id}", response_model=MensagemAPI)
async def remover(
    deposito_id: UUID,
    usuario: Usuario = Depends(exigir_perfis(PerfilCodigo.GESTAO)),
    sessao: AsyncSession = Depends(sessao_db),
) -> MensagemAPI:
    repositorio = RepositorioDeposito(sessao)
    deposito = await repositorio.buscar(deposito_id)
    if deposito is None:
        raise ErroApp("Deposito nao encontrado.", status_code=404, codigo="nao_encontrado")
    # Inativa em vez de excluir fisicamente, preservando o historico de produtos/movimentacoes.
    await repositorio.editar(deposito, {"ativo": False})
    return MensagemAPI(mensagem="Deposito desativado.")

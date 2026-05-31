from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db, usuario_atual
from src.esquemas import (
    CadastroEntrada,
    EntrarEntrada,
    MensagemAPI,
    NovaSenhaEntrada,
    RecuperarSenhaEntrada,
    TokenSaida,
    UsuarioSaida,
    ValidarCodigoEntrada,
)
from src.modelos import Usuario
from src.servicos import ServicoAutenticacao

router = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])


@router.post("/cadastro", response_model=TokenSaida)
async def cadastrar(dados: CadastroEntrada, sessao: AsyncSession = Depends(sessao_db)) -> TokenSaida:
    return await ServicoAutenticacao(sessao).cadastrar(dados)


@router.post("/entrar", response_model=TokenSaida)
async def entrar(dados: EntrarEntrada, sessao: AsyncSession = Depends(sessao_db)) -> TokenSaida:
    return await ServicoAutenticacao(sessao).entrar(dados)


@router.post("/recuperar-senha", response_model=MensagemAPI)
async def recuperar_senha(
    dados: RecuperarSenhaEntrada,
    sessao: AsyncSession = Depends(sessao_db),
) -> MensagemAPI:
    mensagem = await ServicoAutenticacao(sessao).recuperar_senha(dados)
    return MensagemAPI(mensagem=mensagem)


@router.post("/validar-codigo", response_model=MensagemAPI)
async def validar_codigo(
    dados: ValidarCodigoEntrada,
    sessao: AsyncSession = Depends(sessao_db),
) -> MensagemAPI:
    await ServicoAutenticacao(sessao).validar_codigo(dados)
    return MensagemAPI(mensagem="Codigo validado.")


@router.put("/nova-senha", response_model=MensagemAPI)
async def nova_senha(
    dados: NovaSenhaEntrada,
    sessao: AsyncSession = Depends(sessao_db),
) -> MensagemAPI:
    await ServicoAutenticacao(sessao).nova_senha(dados)
    return MensagemAPI(mensagem="Senha redefinida.")


@router.get("/perfil", response_model=UsuarioSaida)
async def perfil(usuario: Usuario = Depends(usuario_atual)) -> UsuarioSaida:
    return UsuarioSaida.de_modelo(usuario)


@router.post("/sair", response_model=MensagemAPI)
async def sair() -> MensagemAPI:
    return MensagemAPI(mensagem="Sessao encerrada no cliente.")

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencias import sessao_db, usuario_atual
from src.esquemas import CadastroEntrada, EntrarEntrada, MensagemAPI, TokenSaida, UsuarioSaida
from src.modelos import Usuario
from src.servicos import ServicoAutenticacao

router = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])


@router.post("/cadastro", response_model=TokenSaida)
async def cadastrar(dados: CadastroEntrada, sessao: AsyncSession = Depends(sessao_db)) -> TokenSaida:
    return await ServicoAutenticacao(sessao).cadastrar(dados)


@router.post("/entrar", response_model=TokenSaida)
async def entrar(dados: EntrarEntrada, sessao: AsyncSession = Depends(sessao_db)) -> TokenSaida:
    return await ServicoAutenticacao(sessao).entrar(dados)


@router.get("/perfil", response_model=UsuarioSaida)
async def perfil(usuario: Usuario = Depends(usuario_atual)) -> UsuarioSaida:
    return UsuarioSaida.de_modelo(usuario)


@router.post("/sair", response_model=MensagemAPI)
async def sair() -> MensagemAPI:
    return MensagemAPI(mensagem="Sessao encerrada no cliente.")

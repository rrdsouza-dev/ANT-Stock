from fastapi import APIRouter, Depends, Query

from app.auth.dependencias import token_atual, usuario_atual
from app.auth.esquemas import Cadastro, LinkGoogle, Login, Saida, Sessao, TokenGoogle
from app.auth.servico import (
    cadastrar,
    entrar as entrar_usuario,
    retorno_google,
    sair as sair_usuario,
    token_google as token_google_usuario,
    url_google,
)
from app.core.rate_limit import limitar_auth
from app.models.usuario import Usuario


# Rotas de autenticacao de usuario e acesso social.
router = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])


@router.post("/cadastro", response_model=Sessao, dependencies=[Depends(limitar_auth)])
def cadastro(dados: Cadastro) -> Sessao:
    # Cria a conta inicial do usuario por email e senha.
    return cadastrar(dados)


@router.post("/entrar", response_model=Sessao, dependencies=[Depends(limitar_auth)])
def entrar(dados: Login) -> Sessao:
    # Faz o login tradicional usando credenciais locais.
    return entrar_usuario(dados)


@router.get("/google", response_model=LinkGoogle, dependencies=[Depends(limitar_auth)])
def google() -> LinkGoogle:
    # Retorna a URL que deve ser aberta para iniciar o login com Google.
    return url_google()


@router.post(
    "/google/token",
    response_model=Sessao,
    dependencies=[Depends(limitar_auth)],
)
def token_google(dados: TokenGoogle) -> Sessao:
    # Aceita um id_token do Google para login direto pelo backend.
    return token_google_usuario(dados)


@router.get(
    "/google/retorno",
    response_model=Sessao,
    dependencies=[Depends(limitar_auth)],
)
def google_retorno(
    access_token: str = Query(...),
    refresh_token: str | None = Query(default=None),
    token_type: str | None = Query(default=None),
    expires_in: int | None = Query(default=None),
    state: str | None = Query(default=None),
    provider_token: str | None = Query(default=None),
) -> Sessao:
    # Organiza o retorno do fluxo OAuth em um formato util para o frontend.
    return retorno_google(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type=token_type,
        expires_in=expires_in,
        state=state,
        provider_token=provider_token,
    )


@router.get("/perfil", response_model=Usuario)
def perfil(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
    # Exibe o usuario autenticado a partir do token Bearer enviado.
    return usuario


@router.post("/sair", response_model=Saida)
def sair(token: str = Depends(token_atual)) -> Saida:
    # Mantem um ponto central para encerrar a sessao no fluxo da API.
    return sair_usuario(token)

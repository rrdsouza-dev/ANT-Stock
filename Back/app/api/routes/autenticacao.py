from fastapi import APIRouter, Depends, Query

from app.autenticacao.contas import cadastrar, entrar, sair as encerrar_sessao
from app.autenticacao.dependencias import token_atual, usuario_atual
from app.autenticacao.esquemas import Cadastro, LinkGoogle, Login, Saida, Sessao, TokenGoogle
from app.autenticacao.google.fluxo import retorno_google, token_google, url_google
from app.core.rate_limit import limitar_auth
from app.models.comum.usuario import Usuario


router = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])


@router.post("/cadastro", response_model=Sessao, dependencies=[Depends(limitar_auth)])
def cadastro(dados: Cadastro) -> Sessao:
    return cadastrar(dados)


@router.post("/entrar", response_model=Sessao, dependencies=[Depends(limitar_auth)])
def login(dados: Login) -> Sessao:
    return entrar(dados)


@router.get("/google", response_model=LinkGoogle, dependencies=[Depends(limitar_auth)])
def google() -> LinkGoogle:
    return url_google()


@router.post(
    "/google/token",
    response_model=Sessao,
    dependencies=[Depends(limitar_auth)],
)
def google_token(dados: TokenGoogle) -> Sessao:
    return token_google(dados)


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
    return usuario


@router.post("/sair", response_model=Saida)
def sair(token: str = Depends(token_atual)) -> Saida:
    return encerrar_sessao(token)

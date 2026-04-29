from typing import Any

from fastapi import HTTPException, status

from app.auth.esquemas import (
    Cadastro,
    LinkGoogle,
    Login,
    Saida,
    Sessao,
    TokenGoogle,
    Usuario,
)
from app.auth.seguranca import criar_token, ler_token
from app.core.config import get_settings
from app.db.client import SupabaseNotConfiguredError, get_supabase_client


def _cliente():
    try:
        return get_supabase_client()
    except SupabaseNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase nao configurado para autenticacao.",
        ) from exc


def _usuario(dados: Any) -> Usuario | None:
    if not dados:
        return None

    nome = None
    if dados.user_metadata:
        nome = dados.user_metadata.get("nome") or dados.user_metadata.get("name")

    provedor = None
    if dados.identities:
        provedor = dados.identities[0].provider

    return Usuario(
        id=dados.id,
        email=dados.email,
        nome=nome,
        provedor=provedor,
    )


def _sessao(resposta: Any) -> Sessao:
    sessao = resposta.session
    usuario = resposta.user if resposta.user else sessao.user if sessao else None
    token_api = None

    if sessao and usuario:
        token_api = criar_token(
            {
                "sub": usuario.id,
                "email": usuario.email,
                "origem": "ant-stock",
            }
        )

    return Sessao(
        access_token=sessao.access_token if sessao else None,
        refresh_token=sessao.refresh_token if sessao else None,
        token_type=sessao.token_type if sessao else None,
        expira_em=sessao.expires_in if sessao else None,
        token_api=token_api,
        token_provedor=sessao.provider_token if sessao else None,
        usuario=_usuario(usuario),
    )


def cadastrar(dados: Cadastro) -> Sessao:
    # Cria um usuario por email e senha usando o Supabase Auth.
    try:
        resposta = _cliente().auth.sign_up(
            {
                "email": dados.email,
                "password": dados.senha,
                "options": {
                    "data": {
                        "nome": dados.nome,
                    }
                },
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel cadastrar o usuario.",
        ) from exc

    return _sessao(resposta)


def entrar(dados: Login) -> Sessao:
    # Realiza o login tradicional com email e senha.
    try:
        resposta = _cliente().auth.sign_in_with_password(
            {
                "email": dados.email,
                "password": dados.senha,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha invalidos.",
        ) from exc

    return _sessao(resposta)


def url_google() -> LinkGoogle:
    # Monta a URL de redirecionamento do Google com estado assinado por JWT.
    config = get_settings()
    estado = criar_token({"fluxo": "google", "tipo": "oauth"}, minutos=10)
    opcoes: dict[str, Any] = {
        "scopes": config.auth_google_scopes,
        "query_params": {
            "access_type": "offline",
            "prompt": "consent",
            "state": estado,
        },
    }

    if config.auth_google_redirect:
        opcoes["redirect_to"] = config.auth_google_redirect

    try:
        resposta = _cliente().auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": opcoes,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel iniciar o login com Google.",
        ) from exc

    return LinkGoogle(url=resposta.url, estado=estado)


def token_google(dados: TokenGoogle) -> Sessao:
    # Permite autenticar com um id_token emitido pelo Google.
    try:
        resposta = _cliente().auth.sign_in_with_id_token(
            {
                "provider": "google",
                "token": dados.token,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token do Google invalido.",
        ) from exc

    return _sessao(resposta)


def retorno_google(
    access_token: str,
    refresh_token: str | None = None,
    token_type: str | None = None,
    expires_in: int | None = None,
    state: str | None = None,
    provider_token: str | None = None,
) -> Sessao:
    # Normaliza o retorno do fluxo OAuth para o formato interno da API.
    if state:
        carga = ler_token(state)
        if carga.get("fluxo") != "google":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estado OAuth invalido.",
            )

    try:
        resposta = _cliente().auth.get_user(access_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nao foi possivel validar o usuario do Google.",
        ) from exc

    if not resposta or not resposta.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nao foi possivel validar o usuario do Google.",
        )

    token_api = criar_token(
        {
            "sub": resposta.user.id,
            "email": resposta.user.email,
            "origem": "ant-stock",
        }
    )

    return Sessao(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type=token_type,
        expira_em=expires_in,
        token_api=token_api,
        token_provedor=provider_token,
        usuario=_usuario(resposta.user),
    )


def perfil(token: str) -> Usuario:
    # Busca o usuario autenticado a partir do JWT do Supabase.
    try:
        resposta = _cliente().auth.get_user(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao autenticado.",
        ) from exc

    if not resposta or not resposta.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao autenticado.",
        )

    usuario = _usuario(resposta.user)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao autenticado.",
        )

    return usuario


def sair(token: str) -> Saida:
    # No backend atual o encerramento depende do descarte dos tokens no cliente.
    perfil(token)
    return Saida(
        mensagem="Sessao validada. Remova os tokens no cliente para concluir a saida."
    )

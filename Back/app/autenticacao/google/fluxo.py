from typing import Any

from fastapi import HTTPException, status

from app.autenticacao.cliente import cliente_supabase
from app.autenticacao.conversores import montar_sessao, montar_usuario
from app.autenticacao.esquemas import LinkGoogle, Sessao, TokenGoogle
from app.autenticacao.google.estado import criar_estado, validar_estado
from app.autenticacao.seguranca import criar_token
from app.core.config import obter_config


def url_google() -> LinkGoogle:
    config = obter_config()
    estado = criar_estado()
    opcoes = _opcoes_google(estado)

    if config.auth_google_redirect:
        opcoes["redirect_to"] = config.auth_google_redirect

    try:
        resposta = cliente_supabase().auth.sign_in_with_oauth(
            {"provider": "google", "options": opcoes}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel iniciar o login com Google.",
        ) from exc

    return LinkGoogle(url=resposta.url, estado=estado)


def token_google(dados: TokenGoogle) -> Sessao:
    try:
        resposta = cliente_supabase().auth.sign_in_with_id_token(
            {"provider": "google", "token": dados.token}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token do Google invalido.",
        ) from exc

    return montar_sessao(resposta)


def retorno_google(
    access_token: str,
    refresh_token: str | None = None,
    token_type: str | None = None,
    expires_in: int | None = None,
    state: str | None = None,
    provider_token: str | None = None,
) -> Sessao:
    validar_estado(state)
    resposta = _usuario_google(access_token)
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
        usuario=montar_usuario(resposta.user),
    )


def _opcoes_google(estado: str) -> dict[str, Any]:
    return {
        "scopes": obter_config().auth_google_scopes,
        "query_params": {
            "access_type": "offline",
            "prompt": "consent",
            "state": estado,
        },
    }


def _usuario_google(access_token: str):
    try:
        resposta = cliente_supabase().auth.get_user(access_token)
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

    return resposta

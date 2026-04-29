from typing import Any

from fastapi import HTTPException, status

from app.auth.cliente import cliente
from app.auth.conversores import sessao, usuario
from app.auth.esquemas import LinkGoogle, Sessao, TokenGoogle
from app.auth.google.estado import criar_estado, validar_estado
from app.auth.seguranca import criar_token
from app.core.config import get_settings


def url_google() -> LinkGoogle:
    # Monta a URL de redirecionamento do Google com estado assinado por JWT.
    config = get_settings()
    estado = criar_estado()
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
        resposta = cliente().auth.sign_in_with_oauth(
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
        resposta = cliente().auth.sign_in_with_id_token(
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

    return sessao(resposta)


def retorno_google(
    access_token: str,
    refresh_token: str | None = None,
    token_type: str | None = None,
    expires_in: int | None = None,
    state: str | None = None,
    provider_token: str | None = None,
) -> Sessao:
    # Normaliza o retorno do fluxo OAuth para o formato interno da API.
    validar_estado(state)

    try:
        resposta = cliente().auth.get_user(access_token)
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
        usuario=usuario(resposta.user),
    )

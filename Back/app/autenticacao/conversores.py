from typing import Any

from app.autenticacao.esquemas import Sessao
from app.autenticacao.seguranca import criar_token
from app.models.comum.usuario import Usuario


def montar_usuario(dados: Any) -> Usuario | None:
    # Traduz o usuario do Supabase para o modelo usado pela API.
    if not dados:
        return None

    metadados = dados.user_metadata or {}
    identidades = dados.identities or []

    return Usuario(
        id=dados.id,
        email=dados.email,
        nome=metadados.get("nome") or metadados.get("name"),
        provedor=identidades[0].provider if identidades else None,
        perfil=metadados.get("perfil"),
        escopo_id=metadados.get("escopo_id"),
    )


def montar_sessao(resposta: Any) -> Sessao:
    # Normaliza a sessao do Supabase em uma resposta estavel para o frontend.
    sessao_supabase = resposta.session
    dados_usuario = (
        resposta.user
        if resposta.user
        else sessao_supabase.user
        if sessao_supabase
        else None
    )

    return Sessao(
        access_token=sessao_supabase.access_token if sessao_supabase else None,
        refresh_token=sessao_supabase.refresh_token if sessao_supabase else None,
        token_type=sessao_supabase.token_type if sessao_supabase else None,
        expira_em=sessao_supabase.expires_in if sessao_supabase else None,
        token_api=_token_api(sessao_supabase, dados_usuario),
        token_provedor=sessao_supabase.provider_token if sessao_supabase else None,
        usuario=montar_usuario(dados_usuario),
    )


def _token_api(sessao_supabase: Any, dados_usuario: Any) -> str | None:
    if not sessao_supabase or not dados_usuario:
        return None

    return criar_token(
        {
            "sub": dados_usuario.id,
            "email": dados_usuario.email,
            "origem": "ant-stock",
        }
    )

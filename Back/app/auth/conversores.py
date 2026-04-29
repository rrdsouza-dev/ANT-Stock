from typing import Any

from app.auth.esquemas import Sessao
from app.auth.seguranca import criar_token
from app.models.usuario import Usuario


def usuario(dados: Any) -> Usuario | None:
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


def sessao(resposta: Any) -> Sessao:
    sessao_auth = resposta.session
    dados_usuario = (
        resposta.user if resposta.user else sessao_auth.user if sessao_auth else None
    )
    token_api = None

    if sessao_auth and dados_usuario:
        token_api = criar_token(
            {
                "sub": dados_usuario.id,
                "email": dados_usuario.email,
                "origem": "ant-stock",
            }
        )

    return Sessao(
        access_token=sessao_auth.access_token if sessao_auth else None,
        refresh_token=sessao_auth.refresh_token if sessao_auth else None,
        token_type=sessao_auth.token_type if sessao_auth else None,
        expira_em=sessao_auth.expires_in if sessao_auth else None,
        token_api=token_api,
        token_provedor=sessao_auth.provider_token if sessao_auth else None,
        usuario=usuario(dados_usuario),
    )

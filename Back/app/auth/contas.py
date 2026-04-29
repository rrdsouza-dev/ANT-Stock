from fastapi import HTTPException, status

from app.auth.cliente import cliente
from app.auth.conversores import sessao, usuario
from app.auth.esquemas import Cadastro, Login, Saida, Sessao
from app.models.usuario import Usuario


def cadastrar(dados: Cadastro) -> Sessao:
    # Cria um usuario por email e senha usando o Supabase Auth.
    try:
        resposta = cliente().auth.sign_up(
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

    return sessao(resposta)


def entrar(dados: Login) -> Sessao:
    # Realiza o login tradicional com email e senha.
    try:
        resposta = cliente().auth.sign_in_with_password(
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

    return sessao(resposta)


def perfil(token: str) -> Usuario:
    # Busca o usuario autenticado a partir do JWT do Supabase.
    try:
        resposta = cliente().auth.get_user(token)
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

    dados = usuario(resposta.user)
    if not dados:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao autenticado.",
        )

    return dados


def sair(token: str) -> Saida:
    # No backend atual o encerramento depende do descarte dos tokens no cliente.
    perfil(token)
    return Saida(
        mensagem="Sessao validada. Remova os tokens no cliente para concluir a saida."
    )

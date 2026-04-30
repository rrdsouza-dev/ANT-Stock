from fastapi import HTTPException, status

from app.autenticacao.cliente import cliente_supabase
from app.autenticacao.conversores import montar_sessao, montar_usuario
from app.autenticacao.esquemas import Cadastro, Login, Saida, Sessao
from app.models.comum.usuario import Usuario


def cadastrar(dados: Cadastro) -> Sessao:
    # Cadastro fica no Supabase Auth; o backend so adapta entrada e saida.
    try:
        resposta = cliente_supabase().auth.sign_up(
            {
                "email": dados.email,
                "password": dados.senha,
                "options": {"data": {"nome": dados.nome}},
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel cadastrar o usuario.",
        ) from exc

    return montar_sessao(resposta)


def entrar(dados: Login) -> Sessao:
    # Login por email e senha usando o provedor nativo do Supabase.
    try:
        resposta = cliente_supabase().auth.sign_in_with_password(
            {"email": dados.email, "password": dados.senha}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha invalidos.",
        ) from exc

    return montar_sessao(resposta)


def buscar_perfil(token: str) -> Usuario:
    # Valida o token no Supabase antes de liberar dados protegidos.
    try:
        resposta = cliente_supabase().auth.get_user(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao autenticado.",
        ) from exc

    usuario = montar_usuario(resposta.user if resposta else None)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao autenticado.",
        )

    return usuario


def sair(token: str) -> Saida:
    buscar_perfil(token)
    return Saida(mensagem="Sessao validada. Remova os tokens no cliente.")

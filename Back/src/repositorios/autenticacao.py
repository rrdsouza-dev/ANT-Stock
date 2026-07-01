from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import col

from src.modelos import CodigoRecuperacao, Perfil, PerfilCodigo, Usuario, UsuarioDeposito
from src.repositorios.base import RepositorioSQL


class RepositorioPerfil(RepositorioSQL[Perfil]):
    modelo = Perfil

    async def por_codigo(self, codigo: PerfilCodigo) -> Perfil | None:
        resultado = await self.sessao.execute(select(Perfil).where(col(Perfil.codigo) == codigo))
        return resultado.scalar_one_or_none()


class RepositorioUsuario(RepositorioSQL[Usuario]):
    modelo = Usuario

    async def buscar(self, item_id: UUID) -> Usuario | None:
        consulta = select(Usuario).options(selectinload(cast(Any, Usuario.perfil))).where(col(Usuario.id) == item_id)
        resultado = await self.sessao.execute(consulta)
        return resultado.scalar_one_or_none()

    async def por_email(self, email: str) -> Usuario | None:
        consulta = select(Usuario).options(selectinload(cast(Any, Usuario.perfil))).where(
            col(Usuario.email) == email.lower()
        )
        resultado = await self.sessao.execute(consulta)
        return resultado.scalar_one_or_none()

    async def listar_com_perfil(self, inicio: int = 0, limite: int = 100) -> list[Usuario]:
        consulta = (
            select(Usuario)
            .options(selectinload(cast(Any, Usuario.perfil)))
            .order_by(col(Usuario.criado_em).desc())
            .offset(inicio)
            .limit(limite)
        )
        resultado = await self.sessao.execute(consulta)
        return list(resultado.scalars().all())


class RepositorioUsuarioDeposito(RepositorioSQL[UsuarioDeposito]):
    modelo = UsuarioDeposito

    async def existe(self, usuario_id: UUID, deposito_id: UUID) -> bool:
        consulta = select(UsuarioDeposito).where(
            col(UsuarioDeposito.usuario_id) == usuario_id,
            col(UsuarioDeposito.deposito_id) == deposito_id,
        )
        resultado = await self.sessao.execute(consulta)
        return resultado.scalar_one_or_none() is not None

    async def vincular_todos_usuarios(self, deposito_id: UUID) -> None:
        """Vincula todos os usuarios ativos ao deposito informado (usado ao criar um deposito novo)."""
        usuarios = await self.sessao.execute(select(Usuario.id).where(col(Usuario.ativo).is_(True)))
        for (usuario_id,) in usuarios.all():
            if not await self.existe(usuario_id, deposito_id):
                self.sessao.add(UsuarioDeposito(usuario_id=usuario_id, deposito_id=deposito_id))
        await self.sessao.commit()

    async def vincular_a_depositos(self, usuario_id: UUID, deposito_ids: list[UUID]) -> None:
        """Vincula um usuario a varios depositos de uma vez (usado no cadastro)."""
        for deposito_id in deposito_ids:
            self.sessao.add(UsuarioDeposito(usuario_id=usuario_id, deposito_id=deposito_id))
        if deposito_ids:
            await self.sessao.commit()


class RepositorioCodigoRecuperacao(RepositorioSQL[CodigoRecuperacao]):
    modelo = CodigoRecuperacao

    async def ultimo_ativo(self, usuario_id: UUID) -> CodigoRecuperacao | None:
        consulta = (
            select(CodigoRecuperacao)
            .where(
                col(CodigoRecuperacao.usuario_id) == usuario_id,
                col(CodigoRecuperacao.usado).is_(False),
            )
            .order_by(col(CodigoRecuperacao.criado_em).desc())
        )
        resultado = await self.sessao.execute(consulta)
        return resultado.scalars().first()

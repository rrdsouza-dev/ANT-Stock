from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col

from src.modelos import (
    CadastroPendente,
    CodigoRecuperacao,
    HistoricoAprovacao,
    HistoricoRecusa,
    Perfil,
    PerfilCodigo,
    StatusCadastro,
    Usuario,
    UsuarioDeposito,
)
from src.repositorios.base import RepositorioSQL


class RepositorioPerfil(RepositorioSQL[Perfil]):
    modelo = Perfil

    async def por_codigo(self, codigo: PerfilCodigo) -> Perfil | None:
        resultado = await self.sessao.execute(select(Perfil).where(col(Perfil.codigo) == codigo))
        return resultado.scalar_one_or_none()


class RepositorioUsuario(RepositorioSQL[Usuario]):
    modelo = Usuario

    def __init__(self, sessao: AsyncSession) -> None:
        super().__init__(sessao)

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


class RepositorioCadastroPendente(RepositorioSQL[CadastroPendente]):
    modelo = CadastroPendente

    async def por_email(self, email: str) -> CadastroPendente | None:
        consulta = select(CadastroPendente).where(col(CadastroPendente.email) == email.lower())
        resultado = await self.sessao.execute(consulta)
        return resultado.scalar_one_or_none()

    async def pendente_por_email(self, email: str) -> CadastroPendente | None:
        consulta = select(CadastroPendente).where(
            col(CadastroPendente.email) == email.lower(),
            col(CadastroPendente.status) == StatusCadastro.PENDENTE,
        )
        resultado = await self.sessao.execute(consulta)
        return resultado.scalar_one_or_none()

    async def listar_pendentes(self, inicio: int = 0, limite: int = 100) -> list[CadastroPendente]:
        consulta = (
            select(CadastroPendente)
            .where(col(CadastroPendente.status) == StatusCadastro.PENDENTE)
            .order_by(col(CadastroPendente.criado_em).desc())
            .offset(inicio)
            .limit(limite)
        )
        resultado = await self.sessao.execute(consulta)
        return list(resultado.scalars().all())


class RepositorioHistoricoAprovacao(RepositorioSQL[HistoricoAprovacao]):
    modelo = HistoricoAprovacao


class RepositorioHistoricoRecusa(RepositorioSQL[HistoricoRecusa]):
    modelo = HistoricoRecusa


class RepositorioUsuarioDeposito(RepositorioSQL[UsuarioDeposito]):
    modelo = UsuarioDeposito

    async def existe(self, usuario_id: UUID, deposito_id: UUID) -> bool:
        consulta = select(UsuarioDeposito).where(
            col(UsuarioDeposito.usuario_id) == usuario_id,
            col(UsuarioDeposito.deposito_id) == deposito_id,
        )
        resultado = await self.sessao.execute(consulta)
        return resultado.scalar_one_or_none() is not None


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

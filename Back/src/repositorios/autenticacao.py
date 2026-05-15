from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col

from src.modelos import Perfil, PerfilCodigo, Usuario
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

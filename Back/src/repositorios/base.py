from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

ModeloT = TypeVar("ModeloT", bound=SQLModel)


class RepositorioSQL(Generic[ModeloT]):
    modelo: type[ModeloT]

    def __init__(self, sessao: AsyncSession) -> None:
        self.sessao = sessao

    async def buscar(self, item_id: UUID) -> ModeloT | None:
        return await self.sessao.get(self.modelo, item_id)

    async def listar(
        self,
        *,
        inicio: int = 0,
        limite: int = 100,
        filtros: dict[str, Any] | None = None,
    ) -> list[ModeloT]:
        consulta: Select[tuple[ModeloT]] = select(self.modelo).offset(inicio).limit(limite)
        for campo, valor in (filtros or {}).items():
            if valor is not None:
                consulta = consulta.where(getattr(self.modelo, campo) == valor)
        resultado = await self.sessao.execute(consulta)
        return list(resultado.scalars().all())

    async def criar(self, dados: dict[str, Any]) -> ModeloT:
        item = self.modelo(**dados)
        self.sessao.add(item)
        await self.sessao.commit()
        await self.sessao.refresh(item)
        return item

    async def editar(self, item: ModeloT, dados: dict[str, Any]) -> ModeloT:
        for campo, valor in dados.items():
            setattr(item, campo, valor)
        self.sessao.add(item)
        await self.sessao.commit()
        await self.sessao.refresh(item)
        return item

    async def remover(self, item: ModeloT) -> None:
        await self.sessao.delete(item)
        await self.sessao.commit()

# Servico CRUD generico com tratamento de nao encontrado.
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlmodel import SQLModel

from src.core.errors import AppError
from src.repositories.base import SQLModelRepository

ModelT = TypeVar("ModelT", bound=SQLModel)


class CRUDService(Generic[ModelT]):
    def __init__(self, repository: SQLModelRepository[ModelT], resource_name: str) -> None:
        self.repository = repository
        self.resource_name = resource_name

    async def listar(self, *, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[ModelT]:
        return await self.repository.listar(offset=offset, limit=min(limit, 200), filters=filters)

    async def buscar(self, item_id: UUID) -> ModelT:
        instance = await self.repository.buscar(item_id)
        if instance is None:
            raise AppError(f"{self.resource_name} nao encontrado.", status_code=404, code="not_found")
        return instance

    async def criar(self, payload: dict[str, Any]) -> ModelT:
        return await self.repository.criar(payload)

    async def editar(self, item_id: UUID, payload: dict[str, Any]) -> ModelT:
        instance = await self.buscar(item_id)
        # Em PATCH, campos ausentes ou nulos nao sobrescrevem dados existentes.
        data = {key: value for key, value in payload.items() if value is not None}
        return await self.repository.editar(instance, data)

    async def remover(self, item_id: UUID) -> None:
        instance = await self.buscar(item_id)
        await self.repository.remover(instance)

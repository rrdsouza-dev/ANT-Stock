from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlmodel import SQLModel

from src.core.exceptions import AppError
from src.repositories.base import SQLModelRepository

ModelT = TypeVar("ModelT", bound=SQLModel)


class CRUDService(Generic[ModelT]):
    def __init__(self, repository: SQLModelRepository[ModelT], resource_name: str) -> None:
        self.repository = repository
        self.resource_name = resource_name

    async def list(self, *, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[ModelT]:
        return await self.repository.list(offset=offset, limit=min(limit, 200), filters=filters)

    async def get(self, item_id: UUID) -> ModelT:
        instance = await self.repository.get(item_id)
        if instance is None:
            raise AppError(f"{self.resource_name} nao encontrado.", status_code=404, code="not_found")
        return instance

    async def create(self, payload: dict[str, Any]) -> ModelT:
        return await self.repository.create(payload)

    async def update(self, item_id: UUID, payload: dict[str, Any]) -> ModelT:
        instance = await self.get(item_id)
        data = {key: value for key, value in payload.items() if value is not None}
        return await self.repository.update(instance, data)

    async def delete(self, item_id: UUID) -> None:
        instance = await self.get(item_id)
        await self.repository.delete(instance)

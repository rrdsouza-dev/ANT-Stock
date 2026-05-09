from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

ModelT = TypeVar("ModelT", bound=SQLModel)


class SQLModelRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, item_id: UUID) -> ModelT | None:
        return await self.session.get(self.model, item_id)

    async def list(self, *, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[ModelT]:
        statement: Select[tuple[ModelT]] = select(self.model).offset(offset).limit(limit)
        for key, value in (filters or {}).items():
            if value is not None:
                statement = statement.where(getattr(self.model, key) == value)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(self, payload: dict[str, Any]) -> ModelT:
        instance = self.model(**payload)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelT, payload: dict[str, Any]) -> ModelT:
        for key, value in payload.items():
            setattr(instance, key, value)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.commit()

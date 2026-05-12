# Repositorio de usuarios.
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from src.models import User
from src.repositories.base import SQLModelRepository


class UserRepository(SQLModelRepository[User]):
    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def por_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(col(User.email) == email.lower()))
        return result.scalar_one_or_none()

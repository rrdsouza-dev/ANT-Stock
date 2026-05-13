from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.nucleo.configuracao import configuracao

config = configuracao()

engine = create_async_engine(
    config.url_banco,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessaoLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def abrir_sessao() -> AsyncGenerator[AsyncSession, None]:
    async with SessaoLocal() as sessao:
        yield sessao

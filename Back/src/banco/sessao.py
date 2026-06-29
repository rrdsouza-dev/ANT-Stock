import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.nucleo.configuracao import configuracao

_HOSTS_SSL = ("supabase.co", "pooler.supabase", "supabase.com")


def _ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _criar_engine():
    # Remove query string; parâmetros de conexão são passados via connect_args
    url = configuracao().url_banco.split("?")[0]
    connect_args: dict = {}
    if any(h in url for h in _HOSTS_SSL):
        connect_args["ssl"] = _ssl_context()
    return create_async_engine(
        url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=1800,
    )


engine = _criar_engine()

SessaoLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def abrir_sessao() -> AsyncGenerator[AsyncSession, None]:
    async with SessaoLocal() as sessao:
        yield sessao

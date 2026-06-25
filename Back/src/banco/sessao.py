from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.nucleo.configuracao import configuracao


def _criar_engine():
    config = configuracao()
    url = config.url_banco

    # asyncpg não aceita ?ssl=require na query string — precisa de connect_args
    connect_args = {}
    if "ssl=require" in url or "supabase.co" in url:
        import ssl as _ssl
        ctx = _ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = _ssl.CERT_NONE  # Supabase usa certificado auto-assinado no pooler
        connect_args["ssl"] = ctx

    return create_async_engine(
        url.split("?")[0],  # remove query string — asyncpg não a suporta
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
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

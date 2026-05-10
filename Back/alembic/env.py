from asyncio import run
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel
from src import models  # noqa: F401
from src.core.config import config as app_config

alembic_config = context.config
settings = app_config()
alembic_config.set_main_option("sqlalchemy.url", settings.url_banco)

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

target_metadata = SQLModel.metadata


def migrar_offline() -> None:
    context.configure(
        url=settings.url_banco,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def rodar_migracoes(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def migrar_online() -> None:
    connectable = async_engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(rodar_migracoes)

    await connectable.dispose()


if context.is_offline_mode():
    migrar_offline()
else:
    run(migrar_online())

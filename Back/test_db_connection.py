#!/usr/bin/env python3
"""
Testa a conexão com o banco Supabase.
Execute da pasta Back/:
    python test_db_connection.py
"""
import asyncio
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from dotenv import load_dotenv
env_path = RAIZ / ".env"
if not env_path.exists():
    print(f"ERRO: .env não encontrado em {env_path}")
    sys.exit(1)
load_dotenv(env_path, override=True)

import os
import src.nucleo.configuracao as _cfg_mod
_cfg_mod.configuracao.cache_clear()

from src.nucleo.configuracao import configuracao
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import ssl


async def testar_conexao() -> None:
    config = configuracao()
    url_raw = config.url_banco
    url = url_raw.split("?")[0]  # asyncpg não aceita query string

    print(f"URL (parcial): {url[:70]}…")
    print("Conectando…\n")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    engine = create_async_engine(
        url,
        connect_args={"ssl": ctx},
        pool_pre_ping=True,
    )

    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            ver = result.fetchone()[0]
            print(f"✓ Conexão OK!")
            print(f"  PostgreSQL: {ver[:50]}")

        async with engine.begin() as conn:
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            ))
            tables = [r[0] for r in result.fetchall()]
            if tables:
                print(f"\n✓ Tabelas encontradas ({len(tables)}): {', '.join(tables)}")
            else:
                print("\n⚠ Nenhuma tabela em public. Execute a migration 000_MASTER_RUN_FIRST.sql primeiro.")
    except Exception as exc:
        print(f"✗ Erro: {exc}")
        print()
        print("Dicas:")
        print("  • Use a URL do POOLER (Session mode, porta 5432), não a URL direta do banco")
        print("    Supabase → Project Settings → Database → Connection Pooling → Session mode")
        print("  • Formato correto:")
        print("    postgresql+asyncpg://postgres.REF:SENHA@aws-0-sa-east-1.pooler.supabase.com:5432/postgres")
        print("  • Se a senha tem # ou @, encode: # → %23, @ → %40")
        print("  • Verifique se o projeto Supabase não está pausado")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(testar_conexao())

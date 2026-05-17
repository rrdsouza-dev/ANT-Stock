import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from src.nucleo.configuracao import configuracao


async def testar_conexao() -> None:
    config = configuracao()
    engine = create_async_engine(config.url_banco, pool_pre_ping=True)

    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("select 1"))
            print("Conexao com Supabase OK.")
            print(f"Resultado: {result.fetchone()}")
    except Exception as exc:
        print(f"Erro na conexao: {exc}")
        print("\nVerifique:")
        print("1. DATABASE_URL no .env esta correto?")
        print("2. Credenciais do Supabase estao corretas?")
        print("3. Sua conexao de internet esta funcionando?")
        print("4. Firewall nao esta bloqueando?")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(testar_conexao())

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from src.nucleo.configuracao import configuracao


async def test_connection():
    config = configuracao()

    try:
        # Tentar conectar
        engine = create_async_engine(config.url_banco, echo=True, pool_pre_ping=True)

        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("✓ Conexão com Supabase OK!")
            print(f"Resultado: {result.fetchone()}")

        await engine.dispose()

    except Exception as e:
        print(f"✗ ERRO na conexão: {e}")
        print("\nVerifique:")
        print("1. DATABASE_URL no .env está correto?")
        print("2. Credenciais do Supabase estão corretas?")
        print("3. Sua conexão de internet está funcionando?")
        print("4. Firewall não está bloqueando?")


if __name__ == "__main__":
    asyncio.run(test_connection())

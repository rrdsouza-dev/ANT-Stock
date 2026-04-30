from functools import lru_cache

from supabase import Client, ClientOptions, create_client

from app.core.config import obter_config


class SupabaseNaoConfiguradoErro(RuntimeError):
    pass


@lru_cache
def obter_cliente_supabase() -> Client:
    settings = obter_config()

    if not settings.supabase_url or not settings.supabase_key:
        raise SupabaseNaoConfiguradoErro(
            "Configure SUPABASE_URL and SUPABASE_KEY antes de usar o Supabase."
        )

    # Cliente compartilhado para Auth, PostgREST e Storage do Supabase.
    return create_client(
        settings.supabase_url,
        settings.supabase_key.get_secret_value(),
        options=ClientOptions(
            schema=settings.supabase_schema,
            postgrest_client_timeout=settings.supabase_timeout_seconds,
            storage_client_timeout=settings.supabase_timeout_seconds,
        ),
    )


def supabase_configurado() -> bool:
    return obter_config().supabase_enabled

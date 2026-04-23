from functools import lru_cache

from supabase import Client, ClientOptions, create_client

from app.core.config import get_settings


class SupabaseNotConfiguredError(RuntimeError):
    """Raised when Supabase settings are missing."""


@lru_cache
def get_supabase_client() -> Client:
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_key:
        raise SupabaseNotConfiguredError(
            "Configure SUPABASE_URL and SUPABASE_KEY before using the database layer."
        )

    return create_client(
        settings.supabase_url,
        settings.supabase_key.get_secret_value(),
        options=ClientOptions(
            schema=settings.supabase_schema,
            postgrest_client_timeout=settings.supabase_timeout_seconds,
            storage_client_timeout=settings.supabase_timeout_seconds,
        ),
    )


def is_supabase_configured() -> bool:
    return get_settings().supabase_enabled

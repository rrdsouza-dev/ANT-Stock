# Cliente opcional para acessar APIs do Supabase.
from functools import lru_cache

from supabase import Client, create_client

from src.core.config import config


def _criar_cliente(key: str) -> Client:
    settings = config()
    if settings.supabase_url is None:
        raise RuntimeError("SUPABASE_URL nao configurado.")
    return create_client(str(settings.supabase_url), key)


@lru_cache
def supabase() -> Client:
    settings = config()
    if settings.supabase_anon_key is None:
        raise RuntimeError("SUPABASE_ANON_KEY nao configurado.")
    return _criar_cliente(settings.supabase_anon_key.get_secret_value())


@lru_cache
def supabase_admin() -> Client:
    settings = config()
    if settings.supabase_service_role_key is None:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY nao configurado.")
    return _criar_cliente(settings.supabase_service_role_key.get_secret_value())

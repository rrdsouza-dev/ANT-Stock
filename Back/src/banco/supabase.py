from functools import lru_cache

from supabase import Client, create_client

from src.nucleo.configuracao import configuracao


def _criar_cliente(chave: str) -> Client:
    config = configuracao()
    if config.supabase_url is None:
        raise RuntimeError("SUPABASE_URL nao configurado.")
    return create_client(str(config.supabase_url), chave)


@lru_cache
def cliente_supabase() -> Client:
    config = configuracao()
    if config.supabase_anon_key is None:
        raise RuntimeError("SUPABASE_ANON_KEY nao configurado.")
    return _criar_cliente(config.supabase_anon_key.get_secret_value())


@lru_cache
def cliente_supabase_admin() -> Client:
    config = configuracao()
    if config.supabase_service_role_key is None:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY nao configurado.")
    return _criar_cliente(config.supabase_service_role_key.get_secret_value())

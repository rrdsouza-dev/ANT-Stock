from fastapi import HTTPException, status

from app.db.client import SupabaseNotConfiguredError, get_supabase_client


def cliente():
    try:
        return get_supabase_client()
    except SupabaseNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase nao configurado para autenticacao.",
        ) from exc

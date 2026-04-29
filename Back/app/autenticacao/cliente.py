from fastapi import HTTPException, status

from app.db.client import SupabaseNaoConfiguradoErro, obter_cliente_supabase


def cliente_supabase():
    try:
        return obter_cliente_supabase()
    except SupabaseNaoConfiguradoErro as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase nao configurado.",
        ) from exc

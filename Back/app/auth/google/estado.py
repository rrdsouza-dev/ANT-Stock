from fastapi import HTTPException, status

from app.auth.seguranca import criar_token, ler_token


def criar_estado() -> str:
    return criar_token({"fluxo": "google", "tipo": "oauth"}, minutos=10)


def validar_estado(estado: str | None) -> None:
    if not estado:
        return

    try:
        carga = ler_token(estado)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado OAuth invalido.",
        ) from exc

    if carga.get("fluxo") != "google":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado OAuth invalido.",
        )

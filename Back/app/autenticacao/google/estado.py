from fastapi import HTTPException, status

from app.autenticacao.seguranca import criar_token, ler_token


def criar_estado() -> str:
    return criar_token({"fluxo": "google"}, minutos=10)


def validar_estado(estado: str | None) -> None:
    if not estado:
        return

    try:
        carga = ler_token(estado)
    except ValueError as exc:
        raise _estado_invalido() from exc

    if carga.get("fluxo") != "google":
        raise _estado_invalido()


def _estado_invalido() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Estado OAuth invalido.",
    )

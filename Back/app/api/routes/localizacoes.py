from fastapi import APIRouter


router = APIRouter(prefix="/localizacoes", tags=["Localizacoes"])


@router.get("")
def listar() -> dict[str, str]:
    return {"mensagem": "Listar localizacoes"}


@router.get("/{localizacao_id}")
def obter(localizacao_id: int) -> dict[str, str | int]:
    return {"mensagem": "Obter localizacao", "localizacao_id": localizacao_id}


@router.post("")
def criar() -> dict[str, str]:
    return {"mensagem": "Criar localizacao"}


@router.put("/{localizacao_id}")
def atualizar(localizacao_id: int) -> dict[str, str | int]:
    return {"mensagem": "Atualizar localizacao", "localizacao_id": localizacao_id}


@router.delete("/{localizacao_id}")
def remover(localizacao_id: int) -> dict[str, str | int]:
    return {"mensagem": "Remover localizacao", "localizacao_id": localizacao_id}

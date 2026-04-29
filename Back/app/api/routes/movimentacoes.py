from fastapi import APIRouter


router = APIRouter(prefix="/movimentacoes", tags=["Movimentacoes"])


@router.get("")
def listar() -> dict[str, str]:
    return {"mensagem": "Listar movimentacoes"}


@router.get("/{movimentacao_id}")
def obter(movimentacao_id: int) -> dict[str, str | int]:
    return {"mensagem": "Obter movimentacao", "movimentacao_id": movimentacao_id}


@router.post("/entrada")
def entrada() -> dict[str, str]:
    return {"mensagem": "Registrar entrada"}


@router.post("/saida")
def saida() -> dict[str, str]:
    return {"mensagem": "Registrar saida"}

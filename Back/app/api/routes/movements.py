from fastapi import APIRouter


# Rotas para registrar e consultar movimentacoes do estoque.
router = APIRouter(prefix="/movimentacoes", tags=["Movimentacoes"])


@router.get("")
def list_movements() -> dict[str, str]:
    # Lista o historico geral de movimentacoes.
    return {"message": "Endpoint para listar movimentacoes"}


@router.get("/{movement_id}")
def get_movement(movement_id: int) -> dict[str, str | int]:
    # Busca uma movimentacao especifica pelo identificador.
    return {
        "message": "Endpoint para buscar uma movimentacao",
        "movement_id": movement_id,
    }


@router.post("/entrada")
def create_entry_movement() -> dict[str, str]:
    # Registra a entrada de itens no estoque.
    return {"message": "Endpoint para registrar entrada de estoque"}


@router.post("/saida")
def create_exit_movement() -> dict[str, str]:
    # Registra a saida de itens do estoque.
    return {"message": "Endpoint para registrar saida de estoque"}

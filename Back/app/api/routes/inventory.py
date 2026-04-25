from fastapi import APIRouter


# Rotas de consulta ao estoque consolidado.
router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("")
def get_inventory() -> dict[str, str]:
    # Retorna a visao geral do estoque.
    return {"message": "Endpoint para consultar o estoque"}


@router.get("/{product_id}")
def get_product_inventory(product_id: int) -> dict[str, str | int]:
    # Consulta a disponibilidade de um produto especifico.
    return {
        "message": "Endpoint para consultar o estoque de um produto",
        "product_id": product_id,
    }

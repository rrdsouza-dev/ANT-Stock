from fastapi import APIRouter


# Rotas do CRUD de categorias para classificar produtos.
router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("")
def list_categories() -> dict[str, str]:
    # Lista todas as categorias disponiveis.
    return {"message": "Endpoint para listar categorias"}


@router.get("/{category_id}")
def get_category(category_id: int) -> dict[str, str | int]:
    # Retorna os dados de uma categoria especifica.
    return {
        "message": "Endpoint para buscar uma categoria",
        "category_id": category_id,
    }


@router.post("")
def create_category() -> dict[str, str]:
    # Cria uma nova categoria para organizacao do estoque.
    return {"message": "Endpoint para criar categoria"}


@router.put("/{category_id}")
def update_category(category_id: int) -> dict[str, str | int]:
    # Atualiza uma categoria ja cadastrada.
    return {
        "message": "Endpoint para atualizar categoria",
        "category_id": category_id,
    }


@router.delete("/{category_id}")
def delete_category(category_id: int) -> dict[str, str | int]:
    # Remove uma categoria do sistema.
    return {
        "message": "Endpoint para remover categoria",
        "category_id": category_id,
    }

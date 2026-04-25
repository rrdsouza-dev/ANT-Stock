from fastapi import APIRouter


# Rotas base para o CRUD de produtos.
router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("")
def list_products() -> dict[str, str]:
    # Lista todos os produtos cadastrados no sistema.
    return {"message": "Endpoint para listar produtos"}


@router.get("/{product_id}")
def get_product(product_id: int) -> dict[str, str | int]:
    # Busca um produto especifico pelo identificador informado.
    return {"message": "Endpoint para buscar um produto", "product_id": product_id}


@router.post("")
def create_product() -> dict[str, str]:
    # Cria um novo produto no estoque.
    return {"message": "Endpoint para criar produto"}


@router.put("/{product_id}")
def update_product(product_id: int) -> dict[str, str | int]:
    # Atualiza os dados de um produto ja existente.
    return {"message": "Endpoint para atualizar produto", "product_id": product_id}


@router.delete("/{product_id}")
def delete_product(product_id: int) -> dict[str, str | int]:
    # Remove um produto do cadastro.
    return {"message": "Endpoint para remover produto", "product_id": product_id}

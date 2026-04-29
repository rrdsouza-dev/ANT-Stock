from fastapi import APIRouter


router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("")
def listar() -> dict[str, str]:
    return {"mensagem": "Listar categorias"}


@router.get("/{categoria_id}")
def obter(categoria_id: int) -> dict[str, str | int]:
    return {"mensagem": "Obter categoria", "categoria_id": categoria_id}


@router.post("")
def criar() -> dict[str, str]:
    return {"mensagem": "Criar categoria"}


@router.put("/{categoria_id}")
def atualizar(categoria_id: int) -> dict[str, str | int]:
    return {"mensagem": "Atualizar categoria", "categoria_id": categoria_id}


@router.delete("/{categoria_id}")
def remover(categoria_id: int) -> dict[str, str | int]:
    return {"mensagem": "Remover categoria", "categoria_id": categoria_id}

from fastapi import APIRouter


router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("")
def geral() -> dict[str, str]:
    return {"mensagem": "Consultar estoque"}


@router.get("/{produto_id}")
def por_produto(produto_id: int) -> dict[str, str | int]:
    return {"mensagem": "Consultar estoque do produto", "produto_id": produto_id}

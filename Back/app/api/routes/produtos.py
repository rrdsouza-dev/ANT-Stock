from fastapi import APIRouter


router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("")
def listar() -> dict[str, str]:
    return {"mensagem": "Listar produtos"}


@router.get("/{produto_id}")
def obter(produto_id: int) -> dict[str, str | int]:
    return {"mensagem": "Obter produto", "produto_id": produto_id}


@router.post("")
def criar() -> dict[str, str]:
    return {"mensagem": "Criar produto"}


@router.put("/{produto_id}")
def atualizar(produto_id: int) -> dict[str, str | int]:
    return {"mensagem": "Atualizar produto", "produto_id": produto_id}


@router.delete("/{produto_id}")
def remover(produto_id: int) -> dict[str, str | int]:
    return {"mensagem": "Remover produto", "produto_id": produto_id}

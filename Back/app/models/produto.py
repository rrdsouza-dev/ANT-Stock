from app.models.base import RegistroDB


class ProdutoDB(RegistroDB):
    nome: str
    sku: str | None = None
    categoria_id: str | None = None
    localizacao_id: str | None = None
    quantidade_minima: int = 0
    ativo: bool = True

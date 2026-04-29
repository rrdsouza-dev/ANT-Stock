from app.models.base import RegistroDB


class EstoqueDB(RegistroDB):
    produto_id: str
    localizacao_id: str | None = None
    quantidade: int = 0

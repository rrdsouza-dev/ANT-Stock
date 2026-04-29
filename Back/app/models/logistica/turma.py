from app.models.comum.base import RegistroDB


class TurmaLogisticaDB(RegistroDB):
    escola_id: str
    nome: str
    ano: int
    periodo: str | None = None
    ativo: bool = True

from app.models.comum.base import RegistroDB


class AlunoLogisticaDB(RegistroDB):
    turma_id: str
    usuario_id: str
    matricula: str | None = None
    ativo: bool = True

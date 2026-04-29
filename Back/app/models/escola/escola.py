from app.models.comum.base import RegistroDB


class EscolaDB(RegistroDB):
    nome: str
    codigo: str | None = None
    cidade: str | None = None
    estado: str | None = None
    ativo: bool = True

from app.models.base import RegistroDB


class CategoriaDB(RegistroDB):
    nome: str
    descricao: str | None = None
    ativo: bool = True

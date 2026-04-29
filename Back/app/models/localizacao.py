from app.models.base import RegistroDB


class LocalizacaoDB(RegistroDB):
    nome: str
    corredor: str | None = None
    prateleira: str | None = None
    posicao: str | None = None
    ativo: bool = True

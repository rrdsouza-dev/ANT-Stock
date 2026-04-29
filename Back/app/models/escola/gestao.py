from app.models.comum.base import RegistroDB


class GestaoEscolaDB(RegistroDB):
    escola_id: str
    usuario_id: str
    cargo: str | None = None
    ativo: bool = True

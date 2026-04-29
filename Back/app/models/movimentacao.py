from datetime import datetime
from typing import Literal

from app.models.base import RegistroDB


class MovimentacaoDB(RegistroDB):
    produto_id: str
    tipo: Literal["entrada", "saida"]
    quantidade: int
    usuario_id: str | None = None
    origem: str | None = None
    destino: str | None = None
    observacao: str | None = None
    movimentado_em: datetime | None = None

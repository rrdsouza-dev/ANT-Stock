from typing import Literal

from app.models.comum.base import RegistroDB


class EstoqueDB(RegistroDB):
    escopo_id: str
    tipo_escopo: Literal["gestao_escola", "turma_logistica"]
    produto_id: str
    localizacao_id: str | None = None
    quantidade: int = 0

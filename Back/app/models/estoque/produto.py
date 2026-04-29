from typing import Literal

from app.models.comum.base import RegistroDB


class ProdutoDB(RegistroDB):
    escopo_id: str
    tipo_escopo: Literal["gestao_escola", "turma_logistica"]
    nome: str
    sku: str | None = None
    categoria_id: str | None = None
    localizacao_id: str | None = None
    quantidade_minima: int = 0
    ativo: bool = True

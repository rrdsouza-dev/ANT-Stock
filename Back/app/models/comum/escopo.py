from typing import Literal

from app.models.comum.base import RegistroDB


class EscopoDB(RegistroDB):
    nome: str
    tipo: Literal["gestao_escola", "turma_logistica"]
    ativo: bool = True

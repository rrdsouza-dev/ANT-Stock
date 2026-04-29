from typing import Literal

from app.models.comum.base import RegistroDB


class LocalizacaoDB(RegistroDB):
    escopo_id: str
    tipo_escopo: Literal["gestao_escola", "turma_logistica"]
    nome: str
    corredor: str | None = None
    prateleira: str | None = None
    posicao: str | None = None
    ativo: bool = True

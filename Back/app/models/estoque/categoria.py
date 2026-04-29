from typing import Literal

from app.models.comum.base import RegistroDB


class CategoriaDB(RegistroDB):
    escopo_id: str
    tipo_escopo: Literal["gestao_escola", "turma_logistica"]
    nome: str
    descricao: str | None = None
    ativo: bool = True

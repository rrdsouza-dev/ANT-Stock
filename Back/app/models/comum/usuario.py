from typing import Literal

from pydantic import BaseModel


class Usuario(BaseModel):
    id: str
    email: str | None = None
    nome: str | None = None
    provedor: str | None = None
    perfil: Literal["gestao", "professor", "aluno"] | None = None
    escopo_id: str | None = None

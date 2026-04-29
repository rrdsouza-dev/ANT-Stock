from pydantic import BaseModel


class Usuario(BaseModel):
    id: str
    email: str | None = None
    nome: str | None = None
    provedor: str | None = None

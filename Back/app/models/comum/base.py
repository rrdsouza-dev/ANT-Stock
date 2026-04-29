from datetime import datetime

from pydantic import BaseModel


class RegistroDB(BaseModel):
    id: str
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None

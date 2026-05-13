from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MensagemAPI(BaseModel):
    mensagem: str


class SchemaComDatas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    criado_em: datetime
    atualizado_em: datetime

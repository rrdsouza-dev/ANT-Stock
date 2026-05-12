# Schemas compartilhados entre respostas da API.
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIMessage(BaseModel):
    message: str


class TimestampedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    created_at: datetime
    updated_at: datetime

# Schemas de autenticacao e leitura de usuario.
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.base import UserProfile


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, alias="nome", min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(alias="senha", min_length=8, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    password: str = Field(alias="senha", min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    email: EmailStr
    name: str | None = Field(default=None, alias="nome")
    provider: str | None = Field(default=None, alias="provedor")
    profile: UserProfile | None = Field(default=None, alias="perfil")
    scope_id: UUID | None = Field(default=None, alias="escopo_id")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead = Field(alias="usuario")

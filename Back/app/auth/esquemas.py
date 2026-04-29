from pydantic import BaseModel, Field

from app.models.usuario import Usuario


class Cadastro(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=8, max_length=128)


class Login(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=8, max_length=128)


class TokenGoogle(BaseModel):
    token: str = Field(min_length=10)


class Sessao(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    expira_em: int | None = None
    token_api: str | None = None
    token_provedor: str | None = None
    usuario: Usuario | None = None


class LinkGoogle(BaseModel):
    url: str
    estado: str


class Saida(BaseModel):
    mensagem: str

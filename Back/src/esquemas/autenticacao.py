from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.modelos import PerfilCodigo, Usuario


class CadastroEntrada(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    perfil: PerfilCodigo = PerfilCodigo.ALUNO


class EntrarEntrada(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class UsuarioSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    auth_id: UUID | None = None
    email: EmailStr
    nome: str | None = None
    provedor: str
    perfil_id: UUID
    perfil: PerfilCodigo | None = None
    ativo: bool

    @classmethod
    def de_modelo(cls, usuario: Usuario) -> "UsuarioSaida":
        perfil = usuario.perfil.codigo if usuario.perfil else None
        return cls(
            id=usuario.id,
            auth_id=usuario.auth_id,
            email=usuario.email,
            nome=usuario.nome,
            provedor=usuario.provedor,
            perfil_id=usuario.perfil_id,
            perfil=perfil,
            ativo=usuario.ativo,
        )


class TokenSaida(BaseModel):
    token: str
    tipo: str = "bearer"
    usuario: UsuarioSaida

import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.modelos import PerfilCodigo, TURMAS_VALIDAS, Usuario

# Regras de senha replicadas no backend (nunca confiar apenas na validacao do front).
_REGEX_MAIUSCULA = re.compile(r"[A-Z]")
_REGEX_DIGITO = re.compile(r"\d")


def _validar_forca_senha(senha: str) -> str:
    if len(senha) < 8:
        raise ValueError("A senha deve ter ao menos 8 caracteres.")
    if not _REGEX_MAIUSCULA.search(senha):
        raise ValueError("A senha deve conter ao menos uma letra maiuscula.")
    if not _REGEX_DIGITO.search(senha):
        raise ValueError("A senha deve conter ao menos um numero.")
    return senha


class CadastroEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    perfil: PerfilCodigo = PerfilCodigo.PROFESSOR
    turmas: list[str] = Field(default_factory=list)

    @field_validator("perfil")
    @classmethod
    def validar_perfil_solicitado(cls, valor: PerfilCodigo) -> PerfilCodigo:
        if valor == PerfilCodigo.ADM:
            raise ValueError("O perfil ADM nao pode ser solicitado pelo cadastro publico.")
        return valor

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        return _validar_forca_senha(valor)

    @field_validator("turmas")
    @classmethod
    def validar_turmas(cls, valor: list[str]) -> list[str]:
        invalidas = [t for t in valor if t not in TURMAS_VALIDAS]
        if invalidas:
            raise ValueError(f"Turma(s) invalida(s): {', '.join(invalidas)}.")
        return valor


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
    turmas: list[str] = Field(default_factory=list)
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
            turmas=usuario.turmas,
            ativo=usuario.ativo,
        )


class TokenSaida(BaseModel):
    token: str
    tipo: str = "bearer"
    usuario: UsuarioSaida


class RecuperarSenhaEntrada(BaseModel):
    email: EmailStr


class ValidarCodigoEntrada(BaseModel):
    email: EmailStr
    codigo: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

    @field_validator("codigo")
    @classmethod
    def validar_codigo_numerico(cls, valor: str) -> str:
        if not valor.isdigit():
            raise ValueError("O codigo deve conter apenas numeros.")
        return valor


class NovaSenhaEntrada(BaseModel):
    email: EmailStr
    codigo: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    nova_senha: str = Field(min_length=8, max_length=128)

    @field_validator("codigo")
    @classmethod
    def validar_codigo_numerico(cls, valor: str) -> str:
        if not valor.isdigit():
            raise ValueError("O codigo deve conter apenas numeros.")
        return valor

    @field_validator("nova_senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        return _validar_forca_senha(valor)

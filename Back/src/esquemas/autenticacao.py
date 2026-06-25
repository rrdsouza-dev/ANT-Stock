from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.modelos import CadastroPendente, HistoricoAprovacao, HistoricoRecusa, PerfilCodigo, StatusCadastro, Usuario


class CadastroEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    perfil: PerfilCodigo = PerfilCodigo.PROFESSOR
    sala: str | None = Field(default=None, max_length=30)

    @field_validator("perfil")
    @classmethod
    def validar_perfil_solicitado(cls, valor: PerfilCodigo) -> PerfilCodigo:
        if valor == PerfilCodigo.ADM:
            raise ValueError("O perfil ADM nao pode ser solicitado pelo cadastro publico.")
        return valor


class CadastroSolicitadoSaida(BaseModel):
    mensagem: str
    status: StatusCadastro = StatusCadastro.PENDENTE


class CadastroPendenteSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    email: EmailStr
    perfil_solicitado: PerfilCodigo
    status: StatusCadastro
    criado_em: datetime

    @classmethod
    def de_modelo(cls, cadastro: CadastroPendente) -> "CadastroPendenteSaida":
        return cls.model_validate(cadastro)


class HistoricoAprovacaoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    nome: str
    email: EmailStr
    perfil: PerfilCodigo
    aprovado_por_id: UUID
    criado_em: datetime


class HistoricoRecusaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    email: EmailStr
    perfil_solicitado: PerfilCodigo
    recusado_por_id: UUID
    motivo: str | None = None
    criado_em: datetime


class AcaoCadastroMassaEntrada(BaseModel):
    ids: list[UUID] = Field(min_length=1, max_length=100)


class RecusarCadastroEntrada(BaseModel):
    motivo: str | None = Field(default=None, max_length=500)


class RecusarCadastroMassaEntrada(AcaoCadastroMassaEntrada):
    motivo: str | None = Field(default=None, max_length=500)


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
    sala: str | None = None
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
            sala=usuario.sala,
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
    nova_senha: str = Field(min_length=6, max_length=128)

    @field_validator("codigo")
    @classmethod
    def validar_codigo_numerico(cls, valor: str) -> str:
        if not valor.isdigit():
            raise ValueError("O codigo deve conter apenas numeros.")
        return valor

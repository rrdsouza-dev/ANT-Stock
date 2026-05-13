from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.esquemas.base import SchemaComDatas
from src.modelos import TipoMovimentacao


class CategoriaEntrada(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)


class CategoriaAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)
    ativo: bool | None = None


class CategoriaSaida(CategoriaEntrada, SchemaComDatas):
    ativo: bool


class LocalizacaoEntrada(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    corredor: str | None = Field(default=None, max_length=50)
    prateleira: str | None = Field(default=None, max_length=50)
    posicao: str | None = Field(default=None, max_length=50)


class LocalizacaoAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    corredor: str | None = Field(default=None, max_length=50)
    prateleira: str | None = Field(default=None, max_length=50)
    posicao: str | None = Field(default=None, max_length=50)
    ativo: bool | None = None


class LocalizacaoSaida(LocalizacaoEntrada, SchemaComDatas):
    ativo: bool


class ProdutoEntrada(BaseModel):
    nome: str = Field(min_length=1, max_length=160)
    codigo: str | None = Field(default=None, max_length=80)
    categoria_id: UUID | None = None
    localizacao_id: UUID | None = None
    quantidade_minima: int = Field(default=0, ge=0)


class ProdutoAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=160)
    codigo: str | None = Field(default=None, max_length=80)
    categoria_id: UUID | None = None
    localizacao_id: UUID | None = None
    quantidade_minima: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class ProdutoSaida(ProdutoEntrada, SchemaComDatas):
    ativo: bool


class EstoqueEntrada(BaseModel):
    produto_id: UUID
    localizacao_id: UUID | None = None
    quantidade: int = Field(default=0, ge=0)


class EstoqueAtualizar(BaseModel):
    localizacao_id: UUID | None = None
    quantidade: int | None = Field(default=None, ge=0)


class EstoqueSaida(EstoqueEntrada, SchemaComDatas):
    pass


class MovimentacaoEntrada(BaseModel):
    produto_id: UUID
    tipo: TipoMovimentacao
    quantidade: int = Field(gt=0)
    usuario_id: UUID | None = None
    pedido_id: UUID | None = None
    origem_id: UUID | None = None
    destino_id: UUID | None = None
    observacao: str | None = Field(default=None, max_length=500)


class MovimentacaoOperacaoEntrada(BaseModel):
    produto_id: UUID
    quantidade: int = Field(gt=0)
    usuario_id: UUID | None = None
    pedido_id: UUID | None = None
    origem_id: UUID | None = None
    destino_id: UUID | None = None
    observacao: str | None = Field(default=None, max_length=500)


class MovimentacaoSaida(MovimentacaoEntrada, SchemaComDatas):
    movimentado_em: datetime

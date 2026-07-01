from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.esquemas.base import SchemaComDatas
from src.modelos import TipoDeposito, TipoMovimentacao


class DepositoEntrada(BaseModel):
    nome: str = Field(min_length=1, max_length=160)
    tipo: TipoDeposito = TipoDeposito.ESCOLAR
    descricao: str | None = Field(default=None, max_length=500)


class DepositoAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=160)
    tipo: TipoDeposito | None = None
    descricao: str | None = Field(default=None, max_length=500)
    ativo: bool | None = None


class DepositoSaida(SchemaComDatas):
    nome: str
    tipo: TipoDeposito
    descricao: str | None = None
    ativo: bool


class CategoriaEntrada(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)


class CategoriaAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)
    ativo: bool | None = None


class CategoriaSaida(SchemaComDatas):
    deposito_id: UUID
    nome: str
    descricao: str | None = None
    ativo: bool


class LocalizacaoEntrada(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    torre: str | None = Field(default=None, max_length=50)
    corredor: str | None = Field(default=None, max_length=50)
    prateleira: str | None = Field(default=None, max_length=50)
    posicao: str | None = Field(default=None, max_length=50)


class LocalizacaoAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    torre: str | None = Field(default=None, max_length=50)
    corredor: str | None = Field(default=None, max_length=50)
    prateleira: str | None = Field(default=None, max_length=50)
    posicao: str | None = Field(default=None, max_length=50)
    ativo: bool | None = None


class LocalizacaoSaida(SchemaComDatas):
    deposito_id: UUID
    nome: str
    torre: str | None = None
    corredor: str | None = None
    prateleira: str | None = None
    posicao: str | None = None
    ativo: bool


class ProdutoEntrada(BaseModel):
    nome: str = Field(min_length=1, max_length=160)
    codigo: str | None = Field(default=None, max_length=80)
    categoria_id: UUID | None = None
    localizacao_id: UUID | None = None
    quantidade_minima: int = Field(default=0, ge=0)
    unidade_medida: str | None = Field(default=None, max_length=30)
    quantidade_por_caixa: int | None = Field(default=None, ge=1)
    lote: str | None = Field(default=None, max_length=80)
    validade: str | None = Field(default=None, max_length=20)
    observacoes: str | None = Field(default=None, max_length=500)


class ProdutoAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=160)
    codigo: str | None = Field(default=None, max_length=80)
    categoria_id: UUID | None = None
    localizacao_id: UUID | None = None
    quantidade_minima: int | None = Field(default=None, ge=0)
    unidade_medida: str | None = Field(default=None, max_length=30)
    quantidade_por_caixa: int | None = Field(default=None, ge=1)
    lote: str | None = Field(default=None, max_length=80)
    validade: str | None = Field(default=None, max_length=20)
    observacoes: str | None = Field(default=None, max_length=500)
    ativo: bool | None = None


class ProdutoSaida(SchemaComDatas):
    deposito_id: UUID
    nome: str
    codigo: str | None = None
    categoria_id: UUID | None = None
    localizacao_id: UUID | None = None
    quantidade_minima: int
    unidade_medida: str | None = None
    quantidade_por_caixa: int | None = None
    lote: str | None = None
    validade: str | None = None
    observacoes: str | None = None
    ativo: bool


class EstoqueEntrada(BaseModel):
    produto_id: UUID
    localizacao_id: UUID | None = None
    quantidade: int = Field(default=0, ge=0)


class EstoqueAtualizar(BaseModel):
    localizacao_id: UUID | None = None
    quantidade: int | None = Field(default=None, ge=0)


class EstoqueSaida(SchemaComDatas):
    deposito_id: UUID
    produto_id: UUID
    localizacao_id: UUID | None = None
    quantidade: int


class MovimentacaoEntrada(BaseModel):
    produto_id: UUID
    tipo: TipoMovimentacao
    quantidade: int = Field(gt=0)
    usuario_id: UUID | None = None
    pedido_id: UUID | None = None
    origem_id: UUID | None = None
    destino_id: UUID | None = None
    lote: str | None = Field(default=None, max_length=80)
    validade_lote: str | None = Field(default=None, max_length=20)
    destino_texto: str | None = Field(default=None, max_length=200)
    observacao: str | None = Field(default=None, max_length=500)


class MovimentacaoOperacaoEntrada(BaseModel):
    produto_id: UUID
    quantidade: int = Field(gt=0)
    usuario_id: UUID | None = None
    pedido_id: UUID | None = None
    origem_id: UUID | None = None
    destino_id: UUID | None = None
    lote: str | None = Field(default=None, max_length=80)
    validade_lote: str | None = Field(default=None, max_length=20)
    destino_texto: str | None = Field(default=None, max_length=200)
    observacao: str | None = Field(default=None, max_length=500)


class MovimentacaoCodigoEntrada(BaseModel):
    codigo: str = Field(min_length=1, max_length=80)
    tipo: TipoMovimentacao
    quantidade: int = Field(gt=0)
    usuario_id: UUID | None = None
    pedido_id: UUID | None = None
    origem_id: UUID | None = None
    destino_id: UUID | None = None
    lote: str | None = Field(default=None, max_length=80)
    validade_lote: str | None = Field(default=None, max_length=20)
    destino_texto: str | None = Field(default=None, max_length=200)
    observacao: str | None = Field(default=None, max_length=500)


class MovimentacaoSaida(SchemaComDatas):
    deposito_id: UUID
    produto_id: UUID
    tipo: TipoMovimentacao
    quantidade: int
    usuario_id: UUID | None = None
    pedido_id: UUID | None = None
    origem_id: UUID | None = None
    destino_id: UUID | None = None
    lote: str | None = None
    validade_lote: str | None = None
    destino_texto: str | None = None
    observacao: str | None = None
    movimentado_em: datetime

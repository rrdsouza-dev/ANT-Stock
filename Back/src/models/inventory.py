from datetime import datetime
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from src.models.base import MovementType, ScopeType, TimestampMixin, UUIDMixin, utcnow


class Category(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "categorias"
    __table_args__ = (UniqueConstraint("scope_id", "name", name="uq_categorias_escopo_nome"),)

    scope_id: UUID = Field(alias="escopo_id", foreign_key="escopos.id", index=True)
    scope_type: ScopeType = Field(alias="tipo_escopo")
    name: str = Field(alias="nome", min_length=1, max_length=120, index=True)
    description: str | None = Field(default=None, alias="descricao", max_length=500)
    active: bool = Field(default=True, alias="ativo")


class Location(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "localizacoes"
    __table_args__ = (UniqueConstraint("scope_id", "name", name="uq_localizacoes_escopo_nome"),)

    scope_id: UUID = Field(alias="escopo_id", foreign_key="escopos.id", index=True)
    scope_type: ScopeType = Field(alias="tipo_escopo")
    name: str = Field(alias="nome", min_length=1, max_length=120, index=True)
    aisle: str | None = Field(default=None, alias="corredor", max_length=50)
    shelf: str | None = Field(default=None, alias="prateleira", max_length=50)
    position: str | None = Field(default=None, alias="posicao", max_length=50)
    active: bool = Field(default=True, alias="ativo")


class Product(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "produtos"
    __table_args__ = (UniqueConstraint("scope_id", "sku", name="uq_produtos_escopo_sku"),)

    scope_id: UUID = Field(alias="escopo_id", foreign_key="escopos.id", index=True)
    scope_type: ScopeType = Field(alias="tipo_escopo")
    name: str = Field(alias="nome", min_length=1, max_length=160, index=True)
    sku: str | None = Field(default=None, max_length=80, index=True)
    category_id: UUID | None = Field(default=None, alias="categoria_id", foreign_key="categorias.id")
    location_id: UUID | None = Field(default=None, alias="localizacao_id", foreign_key="localizacoes.id")
    minimum_quantity: int = Field(default=0, alias="quantidade_minima", ge=0)
    active: bool = Field(default=True, alias="ativo")


class Stock(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "estoques"
    __table_args__ = (
        UniqueConstraint("scope_id", "product_id", "location_id", name="uq_estoques_escopo_produto_local"),
    )

    scope_id: UUID = Field(alias="escopo_id", foreign_key="escopos.id", index=True)
    scope_type: ScopeType = Field(alias="tipo_escopo")
    product_id: UUID = Field(alias="produto_id", foreign_key="produtos.id", index=True)
    location_id: UUID | None = Field(default=None, alias="localizacao_id", foreign_key="localizacoes.id")
    quantity: int = Field(default=0, alias="quantidade", ge=0)


class Movement(UUIDMixin, TimestampMixin, table=True):
    __tablename__ = "movimentacoes"

    scope_id: UUID = Field(alias="escopo_id", foreign_key="escopos.id", index=True)
    scope_type: ScopeType = Field(alias="tipo_escopo")
    product_id: UUID = Field(alias="produto_id", foreign_key="produtos.id", index=True)
    movement_type: MovementType = Field(alias="tipo")
    quantity: int = Field(alias="quantidade", gt=0)
    user_id: UUID | None = Field(default=None, alias="usuario_id", foreign_key="usuarios.id")
    origin: str | None = Field(default=None, alias="origem", max_length=120)
    destination: str | None = Field(default=None, alias="destino", max_length=120)
    note: str | None = Field(default=None, alias="observacao", max_length=500)
    moved_at: datetime = Field(default_factory=utcnow, alias="movimentado_em")

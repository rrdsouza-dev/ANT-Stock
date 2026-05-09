from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.base import MovementType, ScopeType
from src.schemas.common import TimestampedSchema


class ScopedPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scope_id: UUID = Field(alias="escopo_id")
    scope_type: ScopeType = Field(alias="tipo_escopo")


class CategoryCreate(ScopedPayload):
    name: str = Field(alias="nome", min_length=1, max_length=120)
    description: str | None = Field(default=None, alias="descricao", max_length=500)


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, alias="nome", min_length=1, max_length=120)
    description: str | None = Field(default=None, alias="descricao", max_length=500)
    active: bool | None = Field(default=None, alias="ativo")


class CategoryRead(CategoryCreate, TimestampedSchema):
    active: bool = Field(alias="ativo")


class LocationCreate(ScopedPayload):
    name: str = Field(alias="nome", min_length=1, max_length=120)
    aisle: str | None = Field(default=None, alias="corredor", max_length=50)
    shelf: str | None = Field(default=None, alias="prateleira", max_length=50)
    position: str | None = Field(default=None, alias="posicao", max_length=50)


class LocationUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, alias="nome", min_length=1, max_length=120)
    aisle: str | None = Field(default=None, alias="corredor", max_length=50)
    shelf: str | None = Field(default=None, alias="prateleira", max_length=50)
    position: str | None = Field(default=None, alias="posicao", max_length=50)
    active: bool | None = Field(default=None, alias="ativo")


class LocationRead(LocationCreate, TimestampedSchema):
    active: bool = Field(alias="ativo")


class ProductCreate(ScopedPayload):
    name: str = Field(alias="nome", min_length=1, max_length=160)
    sku: str | None = Field(default=None, max_length=80)
    category_id: UUID | None = Field(default=None, alias="categoria_id")
    location_id: UUID | None = Field(default=None, alias="localizacao_id")
    minimum_quantity: int = Field(default=0, alias="quantidade_minima", ge=0)


class ProductUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, alias="nome", min_length=1, max_length=160)
    sku: str | None = Field(default=None, max_length=80)
    category_id: UUID | None = Field(default=None, alias="categoria_id")
    location_id: UUID | None = Field(default=None, alias="localizacao_id")
    minimum_quantity: int | None = Field(default=None, alias="quantidade_minima", ge=0)
    active: bool | None = Field(default=None, alias="ativo")


class ProductRead(ProductCreate, TimestampedSchema):
    active: bool = Field(alias="ativo")


class StockCreate(ScopedPayload):
    product_id: UUID = Field(alias="produto_id")
    location_id: UUID | None = Field(default=None, alias="localizacao_id")
    quantity: int = Field(default=0, alias="quantidade", ge=0)


class StockUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    location_id: UUID | None = Field(default=None, alias="localizacao_id")
    quantity: int | None = Field(default=None, alias="quantidade", ge=0)


class StockRead(StockCreate, TimestampedSchema):
    pass


class MovementCreate(ScopedPayload):
    product_id: UUID = Field(alias="produto_id")
    movement_type: MovementType = Field(alias="tipo")
    quantity: int = Field(alias="quantidade", gt=0)
    user_id: UUID | None = Field(default=None, alias="usuario_id")
    origin: str | None = Field(default=None, alias="origem", max_length=120)
    destination: str | None = Field(default=None, alias="destino", max_length=120)
    note: str | None = Field(default=None, alias="observacao", max_length=500)


class MovementOperationCreate(ScopedPayload):
    product_id: UUID = Field(alias="produto_id")
    quantity: int = Field(alias="quantidade", gt=0)
    user_id: UUID | None = Field(default=None, alias="usuario_id")
    origin: str | None = Field(default=None, alias="origem", max_length=120)
    destination: str | None = Field(default=None, alias="destino", max_length=120)
    note: str | None = Field(default=None, alias="observacao", max_length=500)


class MovementRead(MovementCreate, TimestampedSchema):
    moved_at: datetime | None = None

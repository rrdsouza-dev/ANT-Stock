from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session
from src.schemas import APIMessage, ProductCreate, ProductRead, ProductUpdate
from src.services import InventoryServices

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("", response_model=list[ProductRead])
async def list_products(
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    scope_id: UUID | None = Query(default=None),
) -> list[ProductRead]:
    items = await InventoryServices(session).products.list(offset=offset, limit=limit, filters={"scope_id": scope_id})
    return [ProductRead.model_validate(item) for item in items]


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: UUID, session: AsyncSession = Depends(get_db_session)) -> ProductRead:
    return ProductRead.model_validate(await InventoryServices(session).products.get(product_id))


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, session: AsyncSession = Depends(get_db_session)) -> ProductRead:
    item = await InventoryServices(session).products.create(payload.model_dump())
    return ProductRead.model_validate(item)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> ProductRead:
    item = await InventoryServices(session).products.update(product_id, payload.model_dump(exclude_unset=True))
    return ProductRead.model_validate(item)


@router.delete("/{product_id}", response_model=APIMessage)
async def delete_product(product_id: UUID, session: AsyncSession = Depends(get_db_session)) -> APIMessage:
    await InventoryServices(session).products.delete(product_id)
    return APIMessage(message="Produto removido.")

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session
from src.schemas import APIMessage, StockCreate, StockRead, StockUpdate
from src.services import InventoryServices

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("", response_model=list[StockRead])
async def list_stocks(
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    scope_id: UUID | None = Query(default=None),
) -> list[StockRead]:
    items = await InventoryServices(session).stocks.list(offset=offset, limit=limit, filters={"scope_id": scope_id})
    return [StockRead.model_validate(item) for item in items]


@router.get("/produto/{product_id}", response_model=list[StockRead])
async def get_stock_by_product(product_id: UUID, session: AsyncSession = Depends(get_db_session)) -> list[StockRead]:
    items = await InventoryServices(session).list_stock_by_product(product_id)
    return [StockRead.model_validate(item) for item in items]


@router.post("", response_model=StockRead, status_code=status.HTTP_201_CREATED)
async def create_stock(payload: StockCreate, session: AsyncSession = Depends(get_db_session)) -> StockRead:
    item = await InventoryServices(session).stocks.create(payload.model_dump())
    return StockRead.model_validate(item)


@router.patch("/{stock_id}", response_model=StockRead)
async def update_stock(
    stock_id: UUID,
    payload: StockUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> StockRead:
    item = await InventoryServices(session).stocks.update(stock_id, payload.model_dump(exclude_unset=True))
    return StockRead.model_validate(item)


@router.delete("/{stock_id}", response_model=APIMessage)
async def delete_stock(stock_id: UUID, session: AsyncSession = Depends(get_db_session)) -> APIMessage:
    await InventoryServices(session).stocks.delete(stock_id)
    return APIMessage(message="Estoque removido.")

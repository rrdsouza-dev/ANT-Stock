from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import sessao_db
from src.schemas import APIMessage, StockCreate, StockRead, StockUpdate
from src.services import InventoryServices

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get("", response_model=list[StockRead])
async def listar(
    session: AsyncSession = Depends(sessao_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    scope_id: UUID | None = Query(default=None),
) -> list[StockRead]:
    items = await InventoryServices(session).stocks.listar(offset=offset, limit=limit, filters={"scope_id": scope_id})
    return [StockRead.model_validate(item) for item in items]


@router.get("/produto/{product_id}", response_model=list[StockRead])
async def por_produto(product_id: UUID, session: AsyncSession = Depends(sessao_db)) -> list[StockRead]:
    items = await InventoryServices(session).estoque_do_produto(product_id)
    return [StockRead.model_validate(item) for item in items]


@router.post("", response_model=StockRead, status_code=status.HTTP_201_CREATED)
async def criar(payload: StockCreate, session: AsyncSession = Depends(sessao_db)) -> StockRead:
    item = await InventoryServices(session).stocks.criar(payload.model_dump())
    return StockRead.model_validate(item)


@router.patch("/{stock_id}", response_model=StockRead)
async def editar(
    stock_id: UUID,
    payload: StockUpdate,
    session: AsyncSession = Depends(sessao_db),
) -> StockRead:
    item = await InventoryServices(session).stocks.editar(stock_id, payload.model_dump(exclude_unset=True))
    return StockRead.model_validate(item)


@router.delete("/{stock_id}", response_model=APIMessage)
async def remover(stock_id: UUID, session: AsyncSession = Depends(sessao_db)) -> APIMessage:
    await InventoryServices(session).stocks.remover(stock_id)
    return APIMessage(message="Estoque removido.")

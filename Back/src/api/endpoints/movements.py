from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session
from src.models import MovementType
from src.schemas import MovementCreate, MovementOperationCreate, MovementRead
from src.services import InventoryServices

router = APIRouter(prefix="/movimentacoes", tags=["Movimentacoes"])


@router.get("", response_model=list[MovementRead])
async def list_movements(
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    scope_id: UUID | None = Query(default=None),
) -> list[MovementRead]:
    items = await InventoryServices(session).movements.list(offset=offset, limit=limit, filters={"scope_id": scope_id})
    return [MovementRead.model_validate(item) for item in items]


@router.get("/{movement_id}", response_model=MovementRead)
async def get_movement(movement_id: UUID, session: AsyncSession = Depends(get_db_session)) -> MovementRead:
    return MovementRead.model_validate(await InventoryServices(session).movements.get(movement_id))


@router.post("", response_model=MovementRead, status_code=status.HTTP_201_CREATED)
async def create_movement(payload: MovementCreate, session: AsyncSession = Depends(get_db_session)) -> MovementRead:
    item = await InventoryServices(session).movements.create(payload.model_dump())
    return MovementRead.model_validate(item)


@router.post("/entrada", response_model=MovementRead, status_code=status.HTTP_201_CREATED)
async def register_inbound(
    payload: MovementOperationCreate,
    session: AsyncSession = Depends(get_db_session),
) -> MovementRead:
    data = payload.model_dump()
    data["movement_type"] = MovementType.IN
    item = await InventoryServices(session).movements.create(data)
    return MovementRead.model_validate(item)


@router.post("/saida", response_model=MovementRead, status_code=status.HTTP_201_CREATED)
async def register_outbound(
    payload: MovementOperationCreate,
    session: AsyncSession = Depends(get_db_session),
) -> MovementRead:
    data = payload.model_dump()
    data["movement_type"] = MovementType.OUT
    item = await InventoryServices(session).movements.create(data)
    return MovementRead.model_validate(item)

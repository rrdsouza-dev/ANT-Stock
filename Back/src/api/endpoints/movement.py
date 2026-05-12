# Endpoints para registrar e consultar movimentacoes.
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import sessao_db
from src.models import MovementType
from src.schemas import MovementCreate, MovementOperationCreate, MovementRead
from src.services import InventoryServices

router = APIRouter(prefix="/movimentacoes", tags=["Movimentacoes"])


@router.get("", response_model=list[MovementRead])
async def listar(
    session: AsyncSession = Depends(sessao_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    scope_id: UUID | None = Query(default=None),
) -> list[MovementRead]:
    items = await InventoryServices(session).movements.listar(offset=offset, limit=limit, filters={"scope_id": scope_id})
    return [MovementRead.model_validate(item) for item in items]


@router.get("/{movement_id}", response_model=MovementRead)
async def buscar(movement_id: UUID, session: AsyncSession = Depends(sessao_db)) -> MovementRead:
    return MovementRead.model_validate(await InventoryServices(session).movements.buscar(movement_id))


@router.post("", response_model=MovementRead, status_code=status.HTTP_201_CREATED)
async def criar(payload: MovementCreate, session: AsyncSession = Depends(sessao_db)) -> MovementRead:
    item = await InventoryServices(session).movements.criar(payload.model_dump())
    return MovementRead.model_validate(item)


@router.post("/entrada", response_model=MovementRead, status_code=status.HTTP_201_CREATED)
async def entrada(
    payload: MovementOperationCreate,
    session: AsyncSession = Depends(sessao_db),
) -> MovementRead:
    data = payload.model_dump()
    data["movement_type"] = MovementType.IN
    item = await InventoryServices(session).movements.criar(data)
    return MovementRead.model_validate(item)


@router.post("/saida", response_model=MovementRead, status_code=status.HTTP_201_CREATED)
async def saida(
    payload: MovementOperationCreate,
    session: AsyncSession = Depends(sessao_db),
) -> MovementRead:
    data = payload.model_dump()
    data["movement_type"] = MovementType.OUT
    item = await InventoryServices(session).movements.criar(data)
    return MovementRead.model_validate(item)

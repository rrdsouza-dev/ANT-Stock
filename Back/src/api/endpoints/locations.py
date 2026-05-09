from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session
from src.schemas import APIMessage, LocationCreate, LocationRead, LocationUpdate
from src.services import InventoryServices

router = APIRouter(prefix="/localizacoes", tags=["Localizacoes"])


@router.get("", response_model=list[LocationRead])
async def list_locations(
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    scope_id: UUID | None = Query(default=None),
) -> list[LocationRead]:
    items = await InventoryServices(session).locations.list(offset=offset, limit=limit, filters={"scope_id": scope_id})
    return [LocationRead.model_validate(item) for item in items]


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(location_id: UUID, session: AsyncSession = Depends(get_db_session)) -> LocationRead:
    return LocationRead.model_validate(await InventoryServices(session).locations.get(location_id))


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(payload: LocationCreate, session: AsyncSession = Depends(get_db_session)) -> LocationRead:
    item = await InventoryServices(session).locations.create(payload.model_dump())
    return LocationRead.model_validate(item)


@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: UUID,
    payload: LocationUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> LocationRead:
    item = await InventoryServices(session).locations.update(location_id, payload.model_dump(exclude_unset=True))
    return LocationRead.model_validate(item)


@router.delete("/{location_id}", response_model=APIMessage)
async def delete_location(location_id: UUID, session: AsyncSession = Depends(get_db_session)) -> APIMessage:
    await InventoryServices(session).locations.delete(location_id)
    return APIMessage(message="Localizacao removida.")

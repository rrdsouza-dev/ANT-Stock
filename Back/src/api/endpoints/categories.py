from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session
from src.schemas import APIMessage, CategoryCreate, CategoryRead, CategoryUpdate
from src.services import InventoryServices

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    session: AsyncSession = Depends(get_db_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    scope_id: UUID | None = Query(default=None),
) -> list[CategoryRead]:
    items = await InventoryServices(session).categories.list(
        offset=offset,
        limit=limit,
        filters={"scope_id": scope_id},
    )
    return [CategoryRead.model_validate(item) for item in items]


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: UUID, session: AsyncSession = Depends(get_db_session)) -> CategoryRead:
    return CategoryRead.model_validate(await InventoryServices(session).categories.get(category_id))


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, session: AsyncSession = Depends(get_db_session)) -> CategoryRead:
    item = await InventoryServices(session).categories.create(payload.model_dump())
    return CategoryRead.model_validate(item)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> CategoryRead:
    item = await InventoryServices(session).categories.update(category_id, payload.model_dump(exclude_unset=True))
    return CategoryRead.model_validate(item)


@router.delete("/{category_id}", response_model=APIMessage)
async def delete_category(category_id: UUID, session: AsyncSession = Depends(get_db_session)) -> APIMessage:
    await InventoryServices(session).categories.delete(category_id)
    return APIMessage(message="Categoria removida.")

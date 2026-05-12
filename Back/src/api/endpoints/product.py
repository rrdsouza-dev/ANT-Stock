# Endpoints para gerenciar produtos.
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import sessao_db
from src.schemas import APIMessage, ProductCreate, ProductRead, ProductUpdate
from src.services import InventoryServices

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("", response_model=list[ProductRead])
async def listar(
    session: AsyncSession = Depends(sessao_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    scope_id: UUID | None = Query(default=None),
) -> list[ProductRead]:
    items = await InventoryServices(session).products.listar(offset=offset, limit=limit, filters={"scope_id": scope_id})
    return [ProductRead.model_validate(item) for item in items]


@router.get("/{product_id}", response_model=ProductRead)
async def buscar(product_id: UUID, session: AsyncSession = Depends(sessao_db)) -> ProductRead:
    return ProductRead.model_validate(await InventoryServices(session).products.buscar(product_id))


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def criar(payload: ProductCreate, session: AsyncSession = Depends(sessao_db)) -> ProductRead:
    item = await InventoryServices(session).products.criar(payload.model_dump())
    return ProductRead.model_validate(item)


@router.patch("/{product_id}", response_model=ProductRead)
async def editar(
    product_id: UUID,
    payload: ProductUpdate,
    session: AsyncSession = Depends(sessao_db),
) -> ProductRead:
    item = await InventoryServices(session).products.editar(product_id, payload.model_dump(exclude_unset=True))
    return ProductRead.model_validate(item)


@router.delete("/{product_id}", response_model=APIMessage)
async def remover(product_id: UUID, session: AsyncSession = Depends(sessao_db)) -> APIMessage:
    await InventoryServices(session).products.remover(product_id)
    return APIMessage(message="Produto removido.")

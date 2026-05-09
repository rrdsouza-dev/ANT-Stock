from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db_session
from src.models import User
from src.schemas import APIMessage, LoginRequest, RegisterRequest, TokenResponse, UserRead
from src.services import AuthService

router = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])


@router.post("/cadastro", response_model=TokenResponse)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_db_session)) -> TokenResponse:
    return await AuthService(session).register(payload)


@router.post("/entrar", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db_session)) -> TokenResponse:
    return await AuthService(session).login(payload)


@router.get("/perfil", response_model=UserRead)
async def profile(user: User = Depends(get_current_user)) -> User:
    return user


@router.post("/sair", response_model=APIMessage)
async def logout() -> APIMessage:
    return APIMessage(message="Sessao encerrada no cliente.")

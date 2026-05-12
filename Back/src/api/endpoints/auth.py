# Endpoints de autenticacao e usuario atual.
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import sessao_db, usuario_atual
from src.models import User
from src.schemas import APIMessage, LoginRequest, RegisterRequest, TokenResponse, UserRead
from src.services import AuthService

router = APIRouter(prefix="/autenticacao", tags=["Autenticacao"])


@router.post("/cadastro", response_model=TokenResponse)
async def cadastrar(payload: RegisterRequest, session: AsyncSession = Depends(sessao_db)) -> TokenResponse:
    return await AuthService(session).cadastrar(payload)


@router.post("/entrar", response_model=TokenResponse)
async def entrar(payload: LoginRequest, session: AsyncSession = Depends(sessao_db)) -> TokenResponse:
    return await AuthService(session).entrar(payload)


@router.get("/perfil", response_model=UserRead)
async def perfil(user: User = Depends(usuario_atual)) -> User:
    return user


@router.post("/sair", response_model=APIMessage)
async def sair() -> APIMessage:
    return APIMessage(message="Sessao encerrada no cliente.")

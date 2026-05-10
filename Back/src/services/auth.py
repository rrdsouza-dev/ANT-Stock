from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppError
from src.core.security import checar_senha, criar_token, gerar_hash
from src.models import User
from src.repositories.users import UserRepository
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)

    async def cadastrar(self, payload: RegisterRequest) -> TokenResponse:
        existing = await self.users.por_email(str(payload.email))
        if existing:
            raise AppError("Email ja cadastrado.", status_code=409, code="email_in_use")

        user = await self.users.criar(
            {
                "email": str(payload.email).lower(),
                "name": payload.name,
                "password_hash": gerar_hash(payload.password),
                "provider": "local",
                "active": True,
            }
        )
        return self._resposta_token(user)

    async def entrar(self, payload: LoginRequest) -> TokenResponse:
        user = await self.users.por_email(str(payload.email))
        if not user or not checar_senha(payload.password, user.password_hash):
            raise AppError("Email ou senha invalidos.", status_code=401, code="invalid_credentials")
        if not user.active:
            raise AppError("Usuario inativo.", status_code=403, code="inactive_user")
        return self._resposta_token(user)

    def _resposta_token(self, user: User) -> TokenResponse:
        token = criar_token(str(user.id), {"email": user.email})
        return TokenResponse(access_token=token, usuario=user)

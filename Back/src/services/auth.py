from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppError
from src.core.security import create_access_token, hash_password, verify_password
from src.models import User
from src.repositories.users import UserRepository
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)

    async def register(self, payload: RegisterRequest) -> TokenResponse:
        existing = await self.users.get_by_email(str(payload.email))
        if existing:
            raise AppError("Email ja cadastrado.", status_code=409, code="email_in_use")

        user = await self.users.create(
            {
                "email": str(payload.email).lower(),
                "name": payload.name,
                "password_hash": hash_password(payload.password),
                "provider": "local",
                "active": True,
            }
        )
        return self._token_response(user)

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self.users.get_by_email(str(payload.email))
        if not user or not verify_password(payload.password, user.password_hash):
            raise AppError("Email ou senha invalidos.", status_code=401, code="invalid_credentials")
        if not user.active:
            raise AppError("Usuario inativo.", status_code=403, code="inactive_user")
        return self._token_response(user)

    def _token_response(self, user: User) -> TokenResponse:
        token = create_access_token(str(user.id), {"email": user.email})
        return TokenResponse(access_token=token, usuario=user)

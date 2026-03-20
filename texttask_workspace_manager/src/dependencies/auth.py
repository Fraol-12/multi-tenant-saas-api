# src/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from src.core.security import decode_access_token
from src.models.user import User
from src.repositories.user import UserRepository
from src.dependencies.repository import get_user_repository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",  # Swagger will show login button
    scheme_name="Bearer",
    description="JWT Bearer token",
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Dependency: extracts and validates current user from JWT Bearer token.
    Raises 401 if token invalid/expired/missing.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await user_repo.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user
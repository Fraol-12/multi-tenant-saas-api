from typing import Annotated

from fastapi import Depends

from src.database import get_db
from src.repositories.user import UserRepository


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> UserRepository:
    """Factory that creates UserRepository bound to current request session."""
    return UserRepository(session=session)
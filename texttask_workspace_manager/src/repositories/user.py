# src/repositories/user.py
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from src.models.user import User


class UserRepository:
    """Repository for User entity operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by primary key."""
        stmt = select(User).where(User.id == user_id, User.deleted == False)
        result = await self.session.execute(stmt)
        try:
            return result.scalar_one()
        except NoResultFound:
            return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by unique email (case-insensitive)."""
        stmt = select(User).where(
            func.lower(User.email) == email.lower(),
            User.deleted == False
        )
        result = await self.session.execute(stmt)
        try:
            return result.scalar_one()
        except NoResultFound:
            return None

    async def create(self, email: str, password_hash: str, username: Optional[str] = None) -> User:
        """Create a new user (password must already be hashed)."""
        user = User(
            email=email,
            password_hash=password_hash,
            username=username,
        )
        self.session.add(user)
        await self.session.flush()  # get ID without commit
        return user

    async def update_email(self, user: User, new_email: str) -> User:
        """Update user's email (assumes uniqueness already checked)."""
        user.email = new_email
        await self.session.flush()
        return user

    # More methods later: soft_delete, update_password, etc.
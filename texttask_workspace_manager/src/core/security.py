"""
Security utilities: password hashing and JWT handling.
Strictly isolated from business logic and routes.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# JWT
ALGORITHM = "HS256"


# src/core/security.py – add optional workspace_id param
def create_access_token(
    subject: str | Any,
    workspace_id: int | None = None,
    expires_delta: timedelta | None = None,
 ) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    if workspace_id is not None:
        to_encode["wid"] = workspace_id  # workspace ID claim

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode JWT and return payload (or None on failure)."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
            options={"verify_exp": True},
        )
        return payload
    except JWTError:
        return None
    
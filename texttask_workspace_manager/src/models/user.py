# src/models/user.py
from typing import Optional

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from .base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "Core user accounts – unique by email"}

    email: Mapped[str] = mapped_column(
        String(320),                    # generous for RFC 5321 max email length
        unique=True,
        nullable=False,
        index=True,
    )

    username: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),                    # bcrypt/argon2 hash length
        nullable=False,
    )

    # Optional – useful for security/audit
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
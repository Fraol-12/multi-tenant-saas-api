# src/models/base.py
"""
Common base class for all models.
Provides automatic IDs, timestamps, soft-delete flag, and indexes.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Abstract base for all domain models.
    - id: auto-increment PK
    - created_at / updated_at: server-managed timestamps
    - deleted / deleted_at: soft-delete support (filter WHERE deleted = false)
    """

    __abstract__ = True  # Not a real table

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,  # speeds up WHERE deleted = false queries
    )
    
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Helps avoid some detached instance issues in async sessions
    __mapper_args__ = {"eager_defaults": True}
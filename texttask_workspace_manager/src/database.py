# src/database.py
"""
Database setup for async SQLAlchemy 2.0 + asyncpg.

Key principles:
- One shared AsyncEngine (connection pool) created once at startup
- One fresh AsyncSession per HTTP request (via Depends)
- Automatic rollback on unhandled exceptions
- Always close session at the end of request (even on error)
- expire_on_commit=False → prevents detached instance surprises after commit
- No global scoped_session → avoids hidden state and asyncio pitfalls

This is the recommended pattern in 2024/2025 community guides for FastAPI + SQLAlchemy async.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # optional – see notes below

from src.config import settings

# ────────────────────────────────────────────────
# Global (application-lifetime) AsyncEngine
# Created once, shared connection pool
# ────────────────────────────────────────────────
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",               # show SQL in dev console
    echo_pool=settings.environment == "development",          # show pool events
    pool_pre_ping=True,                                       # detect broken connections
    pool_size=5,                                              # base connections kept open
    max_overflow=10,                                          # extra connections allowed
    pool_timeout=30,                                          # wait time for connection
    # poolclass=NullPool,                                     # ← uncomment if using PgBouncer
    future=True,                                              # enforce 2.0 style
)


# ────────────────────────────────────────────────
# Session factory – blueprint for creating sessions
# expire_on_commit=False is very important for async code
# ────────────────────────────────────────────────
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,          # ← prevents lazy-load after commit
    autoflush=False,                 # we control flushing explicitly
)


# ────────────────────────────────────────────────
# FastAPI dependency: provides one AsyncSession per request
# Usage: async def endpoint(db: AsyncSession = Depends(get_db)):
# ────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that yields a new AsyncSession per request.
    - Rolls back automatically on any unhandled exception
    - Always closes the session at the end (resource cleanup)
    """
    session = async_session_factory()

    try:
        yield session
        # If no exception occurred → commit is caller's responsibility
        # (we do NOT auto-commit here – explicit commit is safer)
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
# alembic/env.py

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config


from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your SQLAlchemy models' MetaData
# (we will create this Base in the next step)
from src.models.base import Base  # ← this line will be added soon

target_metadata = Base.metadata

# ────────────────────────────────────────────────
# Override the default URL handling – use our async engine
# ────────────────────────────────────────────────
def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()

    async def run_async():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    asyncio.run(run_async())

def process_revision_directives(context, revision, directives):
    """Skip empty revisions in autogenerate"""
    if context.config.cmd_opts.autogenerate:
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            print("No changes detected.")


# ────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
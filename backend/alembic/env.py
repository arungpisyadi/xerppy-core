"""
Alembic environment configuration for async SQLAlchemy migrations.

This module configures Alembic to work with async SQLAlchemy models
and supports multiple database types (SQLite, PostgreSQL, MySQL).
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path so we can import 'app' module
# This resolves ModuleNotFoundError when running alembic commands
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection

from alembic import context

from app.config.settings import settings
from app.db.connection import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.built_database_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here too.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    
    For migration purposes, we use sync engine for compatibility.
    """
    # Convert async URL to sync URL
    # Note: We replace the full async dialect prefix to avoid issues like
    # 'mysql+aiomysql' -> 'mysql.mysql' when only partial string is replaced
    db_url = settings.built_database_url
    if "+aiosqlite://" in db_url:
        sync_url = db_url.replace("sqlite+aiosqlite://", "sqlite://")
    elif "+aiomysql://" in db_url:
        # Convert async MySQL URL to sync with pymysql driver
        # This explicitly uses pymysql instead of default mysqldb
        sync_url = db_url.replace("mysql+aiomysql://", "mysql+pymysql://")
    elif "+asyncpg://" in db_url:
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    else:
        sync_url = db_url
    
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
        )
        connection.commit()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

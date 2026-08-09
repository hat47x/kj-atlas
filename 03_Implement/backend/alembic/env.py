from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

# CI may export legacy DATABASE_URL for unrelated services.
# ENV-ARCH-01 enforces KJ_ATLAS_* only, so remove legacy key before importing app settings.
os.environ.pop("DATABASE_URL", None)

from kj_atlas_api.db import _normalize_database_url
from kj_atlas_api.models import Base
from kj_atlas_api.persistence_shapes import install_portable_text_ddl_hook
from kj_atlas_api.settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", _normalize_database_url(settings.database_url))

target_metadata = Base.metadata
install_portable_text_ddl_hook()


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

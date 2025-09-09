
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context


# Імпортуємо моделі та URL бази даних
from src.database.models import Base
from src.database.db import DATABASE_URL


# Конфігурація Alembic
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)


# Налаштування логування
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Метадані моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск міграцій у 'офлайн' режимі."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск міграцій у 'онлайн' режимі."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Вибір режиму запуску
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

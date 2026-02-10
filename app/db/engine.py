"""Async-движок SQLAlchemy и фабрика сессий."""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Создаём директорию для БД, если её нет
_db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
if _db_path:
    Path(_db_path).parent.mkdir(parents=True, exist_ok=True)

# Async-движок
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

# Фабрика сессий
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Инициализация базы данных — создание всех таблиц."""
    from app.db.models.base import Base  # noqa: F811

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

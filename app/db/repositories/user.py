"""Репозиторий пользователей — CRUD-операции для модели User."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    """Получить пользователя по Telegram ID."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    first_name: str,
    username: str | None = None,
) -> User:
    """Создать нового пользователя."""
    user = User(
        telegram_id=telegram_id,
        first_name=first_name,
        username=username,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_couple(
    session: AsyncSession,
    user: User,
    couple_id: int,
) -> User:
    """Привязать пользователя к паре."""
    user.couple_id = couple_id
    await session.commit()
    await session.refresh(user)
    return user

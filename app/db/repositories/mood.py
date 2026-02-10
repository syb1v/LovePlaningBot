"""Репозиторий настроения — CRUD-операции для модели Mood."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.mood import Mood


async def get_today_mood(
    session: AsyncSession,
    user_id: int,
    couple_id: int,
) -> Mood | None:
    """Получить настроение пользователя на сегодня."""
    today = date.today()
    stmt = select(Mood).where(
        Mood.user_id == user_id,
        Mood.couple_id == couple_id,
        Mood.date == today,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def set_mood(
    session: AsyncSession,
    user_id: int,
    couple_id: int,
    emoji: str,
) -> Mood:
    """Установить или обновить настроение на сегодня."""
    today = date.today()
    existing = await get_today_mood(session, user_id, couple_id)

    if existing:
        existing.emoji = emoji
        await session.commit()
        await session.refresh(existing)
        return existing

    mood = Mood(
        user_id=user_id,
        couple_id=couple_id,
        emoji=emoji,
        date=today,
    )
    session.add(mood)
    await session.commit()
    await session.refresh(mood)
    return mood


async def get_partner_mood(
    session: AsyncSession,
    partner_id: int,
    couple_id: int,
) -> Mood | None:
    """Получить настроение партнёра на сегодня."""
    today = date.today()
    stmt = select(Mood).where(
        Mood.user_id == partner_id,
        Mood.couple_id == couple_id,
        Mood.date == today,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

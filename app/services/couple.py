"""Сервис бизнес-логики для пар."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.repositories.couple import get_couple_by_id


async def get_partner(session: AsyncSession, db_user: User) -> User | None:
    """Получить партнёра текущего пользователя."""
    if not db_user.couple_id:
        return None

    couple = await get_couple_by_id(session, db_user.couple_id)
    if not couple:
        return None

    for user in couple.users:
        if user.telegram_id != db_user.telegram_id:
            return user

    return None

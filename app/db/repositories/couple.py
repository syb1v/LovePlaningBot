"""Репозиторий пар — CRUD-операции для модели Couple."""

import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.couple import Couple


def _generate_invite_code() -> str:
    """Сгенерировать уникальный 8-символьный invite-код."""
    return secrets.token_urlsafe(6)  # ~8 символов


async def create_couple(session: AsyncSession) -> Couple:
    """Создать новую пару с уникальным invite-кодом."""
    couple = Couple(invite_code=_generate_invite_code())
    session.add(couple)
    await session.commit()
    await session.refresh(couple)
    return couple


async def get_couple_by_invite_code(
    session: AsyncSession,
    invite_code: str,
) -> Couple | None:
    """Найти пару по invite-коду."""
    stmt = (
        select(Couple)
        .options(selectinload(Couple.users))
        .where(Couple.invite_code == invite_code)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_couple_by_id(
    session: AsyncSession,
    couple_id: int,
) -> Couple | None:
    """Получить пару по ID."""
    stmt = (
        select(Couple)
        .options(selectinload(Couple.users))
        .where(Couple.id == couple_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

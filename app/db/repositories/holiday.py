"""Репозиторий для праздников пары."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.holiday import Holiday


async def get_holidays_by_couple(
    session: AsyncSession, couple_id: int
) -> list[Holiday]:
    """Получить все праздники пары."""
    result = await session.execute(
        select(Holiday)
        .where(Holiday.couple_id == couple_id)
        .order_by(Holiday.month, Holiday.day)
    )
    return list(result.scalars().all())


async def get_holiday_by_id(
    session: AsyncSession, holiday_id: int
) -> Holiday | None:
    """Получить праздник по ID."""
    return await session.get(Holiday, holiday_id)


async def create_holiday(
    session: AsyncSession,
    name: str,
    month: int,
    day: int,
    couple_id: int,
    year: int | None = None,
    remind_before: int = 3,
) -> Holiday:
    """Создать праздник."""
    holiday = Holiday(
        name=name,
        month=month,
        day=day,
        year=year,
        couple_id=couple_id,
        remind_before=remind_before,
    )
    session.add(holiday)
    await session.commit()
    await session.refresh(holiday)
    return holiday


async def delete_holiday(session: AsyncSession, holiday: Holiday) -> None:
    """Удалить праздник."""
    await session.delete(holiday)
    await session.commit()


async def toggle_holiday(session: AsyncSession, holiday: Holiday) -> Holiday:
    """Переключить активность праздника."""
    holiday.is_active = not holiday.is_active
    await session.commit()
    await session.refresh(holiday)
    return holiday

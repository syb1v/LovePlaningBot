"""Сервис планирования — бизнес-логика для элементов плана."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.item import ItemStatus
from app.db.repositories.item import get_items_by_couple


async def get_couple_progress(
    session: AsyncSession,
    couple_id: int,
) -> dict[str, int]:
    """Получить общий прогресс пары."""
    items = await get_items_by_couple(session, couple_id)
    total = len(items)
    done = sum(1 for i in items if i.status == ItemStatus.DONE)
    in_progress = sum(1 for i in items if i.status == ItemStatus.IN_PROGRESS)
    pending = sum(1 for i in items if i.status == ItemStatus.PENDING)

    return {
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "pending": pending,
    }

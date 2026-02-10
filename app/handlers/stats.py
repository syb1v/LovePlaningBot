"""Хендлер статистики — прогресс пары по категориям."""

from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.category import get_categories_by_couple
from app.db.repositories.couple import get_couple_by_id
from app.db.repositories.user import get_user_by_telegram_id
from app.utils import texts
from app.utils.formatting import format_category_progress, format_items_count

router = Router(name="stats")


@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message, session: AsyncSession) -> None:
    """Показать статистику пары."""
    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user or not db_user.couple_id:
        await message.answer(texts.NO_COUPLE, parse_mode="HTML")
        return

    couple = await get_couple_by_id(session, db_user.couple_id)
    categories = await get_categories_by_couple(session, db_user.couple_id)

    # Дней в боте
    days = (datetime.utcnow() - couple.created_at).days if couple else 0

    # Подсчёт элементов
    total, done = format_items_count(categories)

    # Прогресс по категориям
    progress = format_category_progress(categories)

    await message.answer(
        texts.STATS_HEADER.format(
            days=days,
            done=done,
            total=total,
            categories_progress=progress,
        ),
        parse_mode="HTML",
    )

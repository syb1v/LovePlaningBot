"""Хендлер напоминаний — управление и информация о дедлайнах."""

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.item import get_items_with_deadline
from app.db.repositories.user import get_user_by_telegram_id
from app.utils import texts
from app.utils.helpers import format_deadline

router = Router(name="reminders")


@router.message(F.text == "🔔 Напоминания")
async def show_reminders(message: Message, session: AsyncSession) -> None:
    """Показать элементы с дедлайнами."""
    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user or not db_user.couple_id:
        await message.answer(texts.NO_COUPLE, parse_mode="HTML")
        return

    items = await get_items_with_deadline(session, db_user.couple_id)

    if not items:
        await message.answer(
            "🔔 <b>Напоминания</b>\n\nНет элементов с дедлайнами.",
            parse_mode="HTML",
        )
        return

    response = "🔔 <b>Ближайшие дедлайны:</b>\n\n"
    for item in items:
        deadline_str = format_deadline(item.deadline)
        response += f"📌 <b>{item.title}</b>\n{deadline_str}\n"

    await message.answer(response, parse_mode="HTML")

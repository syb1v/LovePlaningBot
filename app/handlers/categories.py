"""Хендлер категорий — просмотр и навигация по категориям."""

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.category import get_categories_by_couple
from app.db.repositories.user import get_user_by_telegram_id
from app.keyboards.inline import categories_keyboard
from app.utils import texts

router = Router(name="categories")


@router.message(F.text == "📋 Планы")
async def show_categories(message: Message, session: AsyncSession) -> None:
    """Показать список категорий пары."""
    db_user = await get_user_by_telegram_id(session, message.from_user.id)

    if not db_user or not db_user.couple_id:
        await message.answer(texts.NO_COUPLE, parse_mode="HTML")
        return

    categories = await get_categories_by_couple(session, db_user.couple_id)

    await message.answer(
        texts.CATEGORIES_HEADER,
        reply_markup=categories_keyboard(categories),
        parse_mode="HTML",
    )

"""Хендлер случайного выбора — «Что посмотреть/поиграть сегодня?»"""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.category import get_categories_by_couple, get_category_by_id
from app.db.repositories.item import get_random_pending_item
from app.db.repositories.user import get_user_by_telegram_id
from app.keyboards.callbacks import RandomCB
from app.keyboards.inline import random_category_keyboard
from app.utils import texts

router = Router(name="random_pick")


@router.message(F.text == "🎲 Рандом")
async def random_pick_menu(message: Message, session: AsyncSession) -> None:
    """Показать меню выбора категории для рандома."""
    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user or not db_user.couple_id:
        await message.answer(texts.NO_COUPLE, parse_mode="HTML")
        return

    categories = await get_categories_by_couple(session, db_user.couple_id)

    await message.answer(
        texts.RANDOM_HEADER,
        reply_markup=random_category_keyboard(categories),
        parse_mode="HTML",
    )


@router.callback_query(RandomCB.filter())
async def do_random_pick(
    callback: CallbackQuery,
    callback_data: RandomCB,
    session: AsyncSession,
) -> None:
    """Выбрать случайный незавершённый элемент."""
    db_user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not db_user or not db_user.couple_id:
        await callback.answer(texts.NO_COUPLE, show_alert=True)
        return

    cat_id = callback_data.category_id if callback_data.category_id != 0 else None
    item = await get_random_pending_item(session, db_user.couple_id, cat_id)

    if item is None:
        await callback.message.edit_text(
            texts.RANDOM_EMPTY, parse_mode="HTML",
        )
    else:
        cat = await get_category_by_id(session, item.category_id)
        icon = cat.icon if cat else "📋"
        cat_name = cat.name if cat else "—"

        await callback.message.edit_text(
            texts.RANDOM_RESULT.format(
                icon=icon,
                title=item.title,
                category=cat_name,
            ),
            parse_mode="HTML",
        )

    await callback.answer()

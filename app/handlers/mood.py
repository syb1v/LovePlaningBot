"""Хендлер настроения — ежедневный эмодзи-статус для пары."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.couple import get_couple_by_id
from app.db.repositories.mood import get_partner_mood, set_mood
from app.db.repositories.user import get_user_by_telegram_id
from app.keyboards.callbacks import MoodCB
from app.keyboards.inline import mood_keyboard
from app.utils import texts

router = Router(name="mood")


@router.message(F.text == "💕 Настроение")
async def show_mood_picker(message: Message, session: AsyncSession) -> None:
    """Показать клавиатуру выбора настроения."""
    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user or not db_user.couple_id:
        await message.answer(texts.NO_COUPLE, parse_mode="HTML")
        return

    await message.answer(
        texts.MOOD_HEADER,
        reply_markup=mood_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(MoodCB.filter())
async def set_mood_handler(
    callback: CallbackQuery,
    callback_data: MoodCB,
    session: AsyncSession,
) -> None:
    """Установить настроение и показать настроение партнёра."""
    db_user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not db_user or not db_user.couple_id:
        await callback.answer(texts.NO_COUPLE, show_alert=True)
        return

    # Сохраняем настроение
    await set_mood(
        session,
        user_id=callback.from_user.id,
        couple_id=db_user.couple_id,
        emoji=callback_data.emoji,
    )

    # Находим партнёра через сессию (не lazy load)
    partner_id = await _get_partner_id(session, db_user)
    partner_line = texts.MOOD_PARTNER_NONE

    if partner_id:
        partner_mood = await get_partner_mood(session, partner_id, db_user.couple_id)
        if partner_mood:
            partner_line = texts.MOOD_PARTNER_LINE.format(
                partner_mood=partner_mood.emoji,
            )

    await callback.message.edit_text(
        texts.MOOD_SET.format(
            my_mood=callback_data.emoji,
            partner_line=partner_line,
        ),
        parse_mode="HTML",
    )
    await callback.answer()


async def _get_partner_id(
    session: AsyncSession, db_user
) -> int | None:
    """Получить telegram_id партнёра через сессию."""
    if not db_user.couple_id:
        return None

    couple = await get_couple_by_id(session, db_user.couple_id)
    if not couple or not couple.users:
        return None

    for user in couple.users:
        if user.telegram_id != db_user.telegram_id:
            return user.telegram_id
    return None

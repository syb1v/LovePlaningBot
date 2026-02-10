"""Хендлер навигации «Назад» через inline-кнопки."""

from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.item import ItemStatus
from app.db.repositories.category import get_categories_by_couple, get_category_by_id
from app.db.repositories.item import get_items_by_category
from app.db.repositories.user import get_user_by_telegram_id
from app.keyboards.callbacks import BackCB
from app.keyboards.inline import categories_keyboard, items_keyboard, settings_keyboard
from app.utils import texts

router = Router(name="back_nav")


@router.callback_query(BackCB.filter())
async def handle_back(
    callback: CallbackQuery,
    callback_data: BackCB,
    session: AsyncSession,
) -> None:
    """Обработать нажатие кнопки «Назад»."""
    target = callback_data.to

    if target == "categories":
        db_user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not db_user or not db_user.couple_id:
            await callback.answer(texts.NO_COUPLE, show_alert=True)
            return

        categories = await get_categories_by_couple(session, db_user.couple_id)
        await callback.message.edit_text(
            texts.CATEGORIES_HEADER,
            reply_markup=categories_keyboard(categories),
            parse_mode="HTML",
        )

    elif target == "category":
        cat_id = callback_data.id
        category = await get_category_by_id(session, cat_id)
        if not category:
            await callback.answer("Категория не найдена", show_alert=True)
            return

        items = await get_items_by_category(session, category.id)
        visible = [i for i in items if not i.is_wishlist]

        done = sum(1 for i in visible if i.status == ItemStatus.DONE)
        in_progress = sum(
            1 for i in visible if i.status == ItemStatus.IN_PROGRESS
        )
        pending = sum(
            1 for i in visible if i.status == ItemStatus.PENDING
        )

        await callback.message.edit_text(
            texts.CATEGORY_ITEMS_HEADER.format(
                icon=category.icon,
                name=category.name,
                total=len(visible),
                done=done,
                in_progress=in_progress,
                pending=pending,
            ),
            reply_markup=items_keyboard(visible, category.id),
            parse_mode="HTML",
        )

    elif target == "settings":
        await callback.message.edit_text(
            "⚙️ <b>Настройки</b>",
            reply_markup=settings_keyboard(),
            parse_mode="HTML",
        )

    elif target == "holidays":
        from app.db.repositories.holiday import get_holidays_by_couple
        from app.keyboards.inline import holidays_keyboard

        db_user = await get_user_by_telegram_id(
            session, callback.from_user.id
        )
        if not db_user or not db_user.couple_id:
            return

        holidays = await get_holidays_by_couple(
            session, db_user.couple_id
        )
        text = "🎉 <b>Праздники</b>\n\n"
        if not holidays:
            text += "Пока нет праздников."
        else:
            text += f"Всего: {len(holidays)}"

        await callback.message.edit_text(
            text,
            reply_markup=holidays_keyboard(
                holidays, db_user.couple_id
            ),
            parse_mode="HTML",
        )

    await callback.answer()

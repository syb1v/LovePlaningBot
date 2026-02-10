"""Хендлер голосования — wishlist с подтверждением партнёром."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.category import get_categories_by_couple, get_category_by_id
from app.db.repositories.item import (
    approve_wishlist_item,
    delete_item,
    get_item_by_id,
    get_wishlist_items,
)
from app.db.repositories.user import get_user_by_telegram_id
from app.keyboards.callbacks import VoteCB
from app.keyboards.inline import categories_keyboard, vote_keyboard
from app.utils import texts

router = Router(name="voting")


@router.message(F.text == "💌 Wishlist")
async def show_wishlist(message: Message, session: AsyncSession) -> None:
    """Показать элементы wishlist и предложить добавить новый."""
    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user or not db_user.couple_id:
        await message.answer(texts.NO_COUPLE, parse_mode="HTML")
        return

    items = await get_wishlist_items(session, db_user.couple_id)

    if not items:
        # Предлагаем добавить
        categories = await get_categories_by_couple(session, db_user.couple_id)
        await message.answer(
            texts.WISHLIST_EMPTY + "\n\nВыбери категорию для предложения:",
            reply_markup=categories_keyboard(categories),
            parse_mode="HTML",
        )
        return

    # Показываем wishlist-элементы
    response = texts.WISHLIST_HEADER + "\n\n"
    for item in items:
        cat = await get_category_by_id(session, item.category_id)
        cat_name = cat.name if cat else "—"
        response += f"💌 <b>{item.title}</b> — 📂 {cat_name}\n"

    await message.answer(response, parse_mode="HTML")

    # Показываем кнопки голосования для чужих предложений
    for item in items:
        if item.added_by_id != message.from_user.id:
            cat = await get_category_by_id(session, item.category_id)
            cat_name = cat.name if cat else "—"
            await message.answer(
                texts.WISHLIST_ITEM.format(
                    title=item.title,
                    category=cat_name,
                    from_name="партнёр",
                ),
                reply_markup=vote_keyboard(item.id),
                parse_mode="HTML",
            )


@router.callback_query(VoteCB.filter())
async def process_vote(
    callback: CallbackQuery,
    callback_data: VoteCB,
    session: AsyncSession,
) -> None:
    """Обработать голос за/против wishlist-элемента."""
    item = await get_item_by_id(session, callback_data.item_id)
    if not item:
        await callback.answer("Элемент не найден", show_alert=True)
        return

    if callback_data.approve:
        await approve_wishlist_item(session, item)
        await callback.message.edit_text(
            texts.WISHLIST_APPROVED.format(title=item.title),
            parse_mode="HTML",
        )
    else:
        title = item.title
        await delete_item(session, item)
        await callback.message.edit_text(
            texts.WISHLIST_REJECTED.format(title=title),
            parse_mode="HTML",
        )

    await callback.answer()

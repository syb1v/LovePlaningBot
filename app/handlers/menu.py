"""Хендлер главного меню — навигация по кнопкам."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.reply import main_menu_keyboard
from app.utils import texts

router = Router(name="menu")


@router.message(F.text == "🔙 Назад")
async def back_to_menu(message: Message, state: FSMContext) -> None:
    """Возврат в главное меню."""
    await state.clear()
    await message.answer(
        texts.MENU,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )

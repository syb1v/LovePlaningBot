"""Reply-клавиатура главного меню."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Планы"),
                KeyboardButton(text="🎲 Рандом"),
            ],
            [
                KeyboardButton(text="💕 Настроение"),
                KeyboardButton(text="📊 Статистика"),
            ],
            [
                KeyboardButton(text="💌 Wishlist"),
                KeyboardButton(text="⚙️ Настройки"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие 💑",
    )


def back_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка «Назад» для возврата в меню."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )

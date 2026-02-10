"""Inline-клавиатуры для различных экранов бота."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models.category import Category
from app.db.models.item import ItemStatus, PlanItem
from app.keyboards.callbacks import (
    BackCB,
    CategoryCB,
    ConfirmCB,
    HolidayCB,
    ItemCB,
    PageCB,
    RandomCB,
    RemindCB,
    SettingsCB,
    StatusCB,
    VoteCB,
)

# Количество элементов на одной странице
PAGE_SIZE = 5

# Эмодзи для статусов
STATUS_EMOJI = {
    ItemStatus.PENDING: "⏳",
    ItemStatus.IN_PROGRESS: "🔄",
    ItemStatus.DONE: "✅",
}

# Эмодзи для настроения

def _back_button(
    to: str, entity_id: int = 0, text: str = "◀️ Назад"
) -> InlineKeyboardButton:
    """Создать кнопку «Назад»."""
    return InlineKeyboardButton(
        text=text,
        callback_data=BackCB(to=to, id=entity_id).pack(),
    )


def categories_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    """Клавиатура выбора категории."""
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=f"{cat.icon} {cat.name}",
            callback_data=CategoryCB(id=cat.id),
        )
    builder.adjust(2)
    return builder.as_markup()


def items_keyboard(
    items: list[PlanItem],
    category_id: int,
    page: int = 0,
) -> InlineKeyboardMarkup:
    """Клавиатура со списком элементов (с пагинацией)."""
    builder = InlineKeyboardBuilder()

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_items = items[start:end]

    for item in page_items:
        emoji = STATUS_EMOJI.get(item.status, "⏳")
        builder.button(
            text=f"{emoji} {item.title}",
            callback_data=ItemCB(id=item.id, action="view"),
        )

    builder.adjust(1)

    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=PageCB(category_id=category_id, page=page - 1).pack(),
            )
        )
    if end < len(items):
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=PageCB(category_id=category_id, page=page + 1).pack(),
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    # Кнопки действий
    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить",
            callback_data=ItemCB(id=category_id, action="add").pack(),
        )
    )
    builder.row(_back_button("categories"))

    return builder.as_markup()


def item_detail_keyboard(item: PlanItem) -> InlineKeyboardMarkup:
    """Клавиатура действий с элементом."""
    builder = InlineKeyboardBuilder()

    # Статусы
    for status in ItemStatus:
        if status != item.status:
            emoji = STATUS_EMOJI[status]
            label_map = {
                ItemStatus.PENDING: "Ожидает",
                ItemStatus.IN_PROGRESS: "В процессе",
                ItemStatus.DONE: "Готово",
            }
            builder.button(
                text=f"{emoji} {label_map[status]}",
                callback_data=StatusCB(
                    item_id=item.id,
                    new_status=status.value,
                ),
            )

    builder.adjust(2)

    # Дополнительные действия
    builder.row(
        InlineKeyboardButton(
            text="✏️ Изменить",
            callback_data=ItemCB(id=item.id, action="edit").pack(),
        ),
        InlineKeyboardButton(
            text="🗓 Дедлайн",
            callback_data=ItemCB(id=item.id, action="deadline").pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="📝 Заметка",
            callback_data=ItemCB(id=item.id, action="notes").pack(),
        ),
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=ItemCB(id=item.id, action="delete").pack(),
        ),
    )

    # Назад к категории
    cat_id = item.category_id if item.category_id else 0
    builder.row(_back_button("category", entity_id=cat_id))

    return builder.as_markup()


def confirm_delete_keyboard(item_id: int) -> InlineKeyboardMarkup:
    """Подтверждение удаления элемента."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Да, удалить",
        callback_data=ConfirmCB(item_id=item_id, action="delete_yes"),
    )
    builder.button(
        text="❌ Отмена",
        callback_data=ConfirmCB(item_id=item_id, action="delete_no"),
    )
    builder.adjust(2)
    return builder.as_markup()



def random_category_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    """Клавиатура выбора категории для рандомного выбора."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🎲 Из всех категорий",
        callback_data=RandomCB(category_id=0),
    )
    for cat in categories:
        builder.button(
            text=f"{cat.icon} {cat.name}",
            callback_data=RandomCB(category_id=cat.id),
        )
    builder.adjust(1)
    return builder.as_markup()


def vote_keyboard(item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура голосования за wishlist-элемент."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Одобрить",
        callback_data=VoteCB(item_id=item_id, approve=True),
    )
    builder.button(
        text="❌ Отклонить",
        callback_data=VoteCB(item_id=item_id, approve=False),
    )
    builder.adjust(2)
    return builder.as_markup()


def settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✏️ Моё имя",
        callback_data=SettingsCB(action="name"),
    )
    builder.button(
        text="🎂 ДР партнёра",
        callback_data=SettingsCB(action="birthday"),
    )
    builder.button(
        text="💕 Дата отношений",
        callback_data=SettingsCB(action="rel_date"),
    )
    builder.button(
        text="🔔 Напоминания",
        callback_data=SettingsCB(action="remind"),
    )
    builder.button(
        text="🎉 Праздники",
        callback_data=SettingsCB(action="holidays"),
    )
    builder.adjust(2)
    return builder.as_markup()


def holidays_keyboard(holidays: list, couple_id: int) -> InlineKeyboardMarkup:
    """Клавиатура списка праздников."""
    builder = InlineKeyboardBuilder()
    for h in holidays:
        status = "✅" if h.is_active else "❌"
        builder.button(
            text=f"{status} {h.name} ({h.day:02d}.{h.month:02d})",
            callback_data=HolidayCB(id=h.id, action="view"),
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(
            text="➕ Добавить праздник",
            callback_data=HolidayCB(id=0, action="add").pack(),
        )
    )
    return builder.as_markup()


def holiday_detail_keyboard(holiday_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Клавиатура действий с праздником."""
    builder = InlineKeyboardBuilder()
    toggle_text = "❌ Выключить" if is_active else "✅ Включить"
    builder.button(
        text=toggle_text,
        callback_data=HolidayCB(id=holiday_id, action="toggle"),
    )
    builder.button(
        text="🗑 Удалить",
        callback_data=HolidayCB(id=holiday_id, action="delete"),
    )
    builder.adjust(2)
    builder.row(_back_button("holidays"))
    return builder.as_markup()


def remind_settings_keyboard(remind_before: int) -> InlineKeyboardMarkup:
    """Клавиатура настройки напоминаний."""
    builder = InlineKeyboardBuilder()
    options = [
        (1, "📅 В день"),
        (2, "1️⃣ За день"),
        (4, "3️⃣ За 3 дня"),
        (8, "7️⃣ За неделю"),
    ]
    for flag, label in options:
        active = "✅" if remind_before & flag else "⬜"
        builder.button(
            text=f"{active} {label}",
            callback_data=RemindCB(flag=flag),
        )
    builder.adjust(2)
    builder.row(_back_button("settings"))
    return builder.as_markup()

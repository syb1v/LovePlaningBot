"""CallbackData фабрики для inline-кнопок."""

from aiogram.filters.callback_data import CallbackData


class CategoryCB(CallbackData, prefix="cat"):
    """Выбор категории."""

    id: int


class ItemCB(CallbackData, prefix="item"):
    """Действия с элементом."""

    id: int
    action: str  # view, status, delete, deadline, notes, edit


class StatusCB(CallbackData, prefix="status"):
    """Изменение статуса элемента."""

    item_id: int
    new_status: str  # pending, in_progress, done


class VoteCB(CallbackData, prefix="vote"):
    """Голосование за/против wishlist-элемента."""

    item_id: int
    approve: bool


class MoodCB(CallbackData, prefix="mood"):
    """Выбор эмодзи настроения."""

    emoji: str


class RandomCB(CallbackData, prefix="rnd"):
    """Рандомный выбор — фильтр по категории."""

    category_id: int  # 0 = из всех


class PageCB(CallbackData, prefix="page"):
    """Пагинация списков."""

    category_id: int
    page: int


class ConfirmCB(CallbackData, prefix="confirm"):
    """Подтверждение действия (удаление и т.д.)."""

    item_id: int
    action: str  # delete_yes, delete_no


class BackCB(CallbackData, prefix="back"):
    """Навигация назад."""

    to: str  # menu, categories, category, item, settings, holidays
    id: int = 0  # ID сущности (категории, элемента и т.д.)


class HolidayCB(CallbackData, prefix="hol"):
    """Действия с праздником."""

    id: int
    action: str  # view, edit, delete, toggle


class SettingsCB(CallbackData, prefix="set"):
    """Действия в настройках."""

    action: str  # name, birthday, rel_date, remind, holidays

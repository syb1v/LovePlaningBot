"""FSM-состояния для диалогов бота."""

from aiogram.fsm.state import State, StatesGroup


class CoupleForm(StatesGroup):
    """Состояния для создания/присоединения к паре."""

    waiting_invite_code = State()


class AddItemForm(StatesGroup):
    """Состояния для добавления нового элемента."""

    waiting_title = State()
    waiting_deadline = State()


class EditItemForm(StatesGroup):
    """Состояния для редактирования элемента."""

    waiting_title = State()


class DeadlineForm(StatesGroup):
    """Состояния для установки дедлайна."""

    waiting_date = State()


class NoteForm(StatesGroup):
    """Состояния для добавления заметки."""

    waiting_note = State()


class WishlistForm(StatesGroup):
    """Состояния для добавления wishlist-элемента."""

    waiting_category = State()
    waiting_title = State()


class NameForm(StatesGroup):
    """Состояния для смены имени."""

    waiting_name = State()


class BirthdayForm(StatesGroup):
    """Состояния для установки ДР."""

    waiting_date = State()


class RelDateForm(StatesGroup):
    """Состояния для даты начала отношений."""

    waiting_date = State()


class HolidayForm(StatesGroup):
    """Состояния для создания праздника."""

    waiting_name = State()
    waiting_date = State()

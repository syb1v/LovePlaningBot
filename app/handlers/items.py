"""Хендлер элементов плана — CRUD, просмотр, изменение статуса, редактирование."""

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.item import ItemStatus
from app.db.repositories.category import get_category_by_id
from app.db.repositories.item import (
    create_item,
    delete_item,
    get_item_by_id,
    get_items_by_category,
    update_item_status,
)
from app.db.repositories.user import get_user_by_telegram_id
from app.keyboards.callbacks import (
    CategoryCB,
    ConfirmCB,
    ItemCB,
    PageCB,
    StatusCB,
)
from app.keyboards.inline import (
    confirm_delete_keyboard,
    item_detail_keyboard,
    items_keyboard,
)
from app.states.forms import AddItemForm, DeadlineForm, EditItemForm, NoteForm
from app.utils import texts
from app.utils.helpers import STATUS_LABELS, format_deadline, format_notes

router = Router(name="items")


# --- Навигация по категориям ---


@router.callback_query(CategoryCB.filter())
async def show_category_items(
    callback: CallbackQuery,
    callback_data: CategoryCB,
    session: AsyncSession,
) -> None:
    """Показать элементы выбранной категории."""
    category = await get_category_by_id(session, callback_data.id)
    if not category:
        await callback.answer("Категория не найдена", show_alert=True)
        return

    items = await get_items_by_category(session, category.id)
    visible_items = [i for i in items if not i.is_wishlist]

    if not visible_items:
        await callback.message.edit_text(
            texts.EMPTY_CATEGORY.format(icon=category.icon, name=category.name),
            reply_markup=items_keyboard([], category.id),
            parse_mode="HTML",
        )
    else:
        done = sum(1 for i in visible_items if i.status == ItemStatus.DONE)
        in_progress = sum(1 for i in visible_items if i.status == ItemStatus.IN_PROGRESS)
        pending = sum(1 for i in visible_items if i.status == ItemStatus.PENDING)

        await callback.message.edit_text(
            texts.CATEGORY_ITEMS_HEADER.format(
                icon=category.icon,
                name=category.name,
                total=len(visible_items),
                done=done,
                in_progress=in_progress,
                pending=pending,
            ),
            reply_markup=items_keyboard(visible_items, category.id),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(PageCB.filter())
async def paginate_items(
    callback: CallbackQuery,
    callback_data: PageCB,
    session: AsyncSession,
) -> None:
    """Пагинация элементов категории."""
    category = await get_category_by_id(session, callback_data.category_id)
    if not category:
        await callback.answer("Категория не найдена", show_alert=True)
        return

    items = await get_items_by_category(session, category.id)
    visible_items = [i for i in items if not i.is_wishlist]

    done = sum(1 for i in visible_items if i.status == ItemStatus.DONE)
    in_progress = sum(1 for i in visible_items if i.status == ItemStatus.IN_PROGRESS)
    pending = sum(1 for i in visible_items if i.status == ItemStatus.PENDING)

    await callback.message.edit_text(
        texts.CATEGORY_ITEMS_HEADER.format(
            icon=category.icon,
            name=category.name,
            total=len(visible_items),
            done=done,
            in_progress=in_progress,
            pending=pending,
        ),
        reply_markup=items_keyboard(visible_items, category.id, callback_data.page),
        parse_mode="HTML",
    )
    await callback.answer()


# --- Просмотр элемента ---


async def _show_item_detail(
    callback: CallbackQuery, session: AsyncSession, item_id: int
) -> None:
    """Показать детали элемента (общая функция)."""
    item = await get_item_by_id(session, item_id)
    if not item:
        await callback.answer("Элемент не найден", show_alert=True)
        return

    await callback.message.edit_text(
        texts.ITEM_DETAIL.format(
            title=item.title,
            category=item.category.name if item.category else "—",
            status=STATUS_LABELS.get(item.status, str(item.status)),
            deadline=format_deadline(item.deadline),
            notes=format_notes(item.notes),
        ),
        reply_markup=item_detail_keyboard(item),
        parse_mode="HTML",
    )


@router.callback_query(ItemCB.filter(F.action == "view"))
async def view_item(
    callback: CallbackQuery,
    callback_data: ItemCB,
    session: AsyncSession,
) -> None:
    """Показать детали элемента."""
    await _show_item_detail(callback, session, callback_data.id)
    await callback.answer()


# --- Изменение статуса ---


@router.callback_query(StatusCB.filter())
async def change_status(
    callback: CallbackQuery,
    callback_data: StatusCB,
    session: AsyncSession,
) -> None:
    """Изменить статус элемента."""
    item = await get_item_by_id(session, callback_data.item_id)
    if not item:
        await callback.answer("Элемент не найден", show_alert=True)
        return

    new_status = ItemStatus(callback_data.new_status)
    await update_item_status(session, item, new_status)

    status_label = STATUS_LABELS.get(new_status, str(new_status))
    await callback.answer(f"Статус: {status_label}")

    # Возвращаем к деталям элемента с обновлённым статусом
    await _show_item_detail(callback, session, item.id)


# --- Добавление нового элемента ---


@router.callback_query(ItemCB.filter(F.action == "add"))
async def add_item_start(
    callback: CallbackQuery,
    callback_data: ItemCB,
    state: FSMContext,
) -> None:
    """Начать процесс добавления элемента."""
    await state.set_state(AddItemForm.waiting_title)
    await state.update_data(category_id=callback_data.id)
    await callback.message.edit_text(texts.ENTER_ITEM_TITLE, parse_mode="HTML")
    await callback.answer()


@router.message(AddItemForm.waiting_title)
async def add_item_title(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Получить название и создать элемент."""
    data = await state.get_data()
    category_id = data["category_id"]
    db_user = await get_user_by_telegram_id(session, message.from_user.id)

    category = await get_category_by_id(session, category_id)
    if not category:
        await message.answer("Категория не найдена.")
        await state.clear()
        return

    await create_item(
        session,
        title=message.text.strip(),
        category_id=category_id,
        couple_id=db_user.couple_id,
        added_by_id=message.from_user.id,
    )

    await state.clear()
    await message.answer(
        texts.ITEM_ADDED.format(title=message.text.strip(), category=category.name),
        parse_mode="HTML",
    )


# --- Редактирование элемента ---


@router.callback_query(ItemCB.filter(F.action == "edit"))
async def edit_item_start(
    callback: CallbackQuery,
    callback_data: ItemCB,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Запросить новое название элемента."""
    item = await get_item_by_id(session, callback_data.id)
    if not item:
        await callback.answer("Элемент не найден", show_alert=True)
        return

    await state.set_state(EditItemForm.waiting_title)
    await state.update_data(item_id=callback_data.id)
    await callback.message.edit_text(
        f"✏️ Текущее название: <b>{item.title}</b>\n\nВведите новое название:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(EditItemForm.waiting_title)
async def edit_item_title(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Сохранить новое название элемента."""
    data = await state.get_data()
    item = await get_item_by_id(session, data["item_id"])

    if not item:
        await message.answer("Элемент не найден.")
        await state.clear()
        return

    old_title = item.title
    item.title = message.text.strip()
    await session.commit()
    await state.clear()

    await message.answer(
        f"✅ Переименовано: <s>{old_title}</s> → <b>{item.title}</b>",
        parse_mode="HTML",
    )


# --- Дедлайн ---


@router.callback_query(ItemCB.filter(F.action == "deadline"))
async def set_deadline_start(
    callback: CallbackQuery,
    callback_data: ItemCB,
    state: FSMContext,
) -> None:
    """Запросить дату дедлайна."""
    await state.set_state(DeadlineForm.waiting_date)
    await state.update_data(item_id=callback_data.id)
    await callback.message.edit_text(texts.ENTER_DEADLINE, parse_mode="HTML")
    await callback.answer()


@router.message(DeadlineForm.waiting_date)
async def process_deadline(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Обработать введённую дату дедлайна."""
    data = await state.get_data()
    item = await get_item_by_id(session, data["item_id"])

    if not item:
        await message.answer("Элемент не найден.")
        await state.clear()
        return

    text = message.text.strip().lower()

    if text in ("нет", "убрать", "удалить", "-"):
        item.deadline = None
        await session.commit()
        await state.clear()
        await message.answer(
            texts.DEADLINE_REMOVED.format(title=item.title),
            parse_mode="HTML",
        )
        return

    try:
        deadline = datetime.strptime(text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer(texts.INVALID_DATE, parse_mode="HTML")
        return

    item.deadline = deadline
    await session.commit()
    await state.clear()

    await message.answer(
        texts.DEADLINE_SET.format(
            title=item.title,
            date=deadline.strftime("%d.%m.%Y"),
        ),
        parse_mode="HTML",
    )


# --- Заметки ---


@router.callback_query(ItemCB.filter(F.action == "notes"))
async def set_notes_start(
    callback: CallbackQuery,
    callback_data: ItemCB,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Запросить текст заметки."""
    item = await get_item_by_id(session, callback_data.id)
    if not item:
        await callback.answer("Элемент не найден", show_alert=True)
        return

    await state.set_state(NoteForm.waiting_note)
    await state.update_data(item_id=callback_data.id)
    await callback.message.edit_text(
        texts.ENTER_NOTE.format(title=item.title),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(NoteForm.waiting_note)
async def process_note(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Сохранить заметку."""
    data = await state.get_data()
    item = await get_item_by_id(session, data["item_id"])

    if not item:
        await message.answer("Элемент не найден.")
        await state.clear()
        return

    item.notes = message.text.strip()
    await session.commit()
    await state.clear()
    await message.answer(texts.NOTE_SAVED, parse_mode="HTML")


# --- Удаление ---


@router.callback_query(ItemCB.filter(F.action == "delete"))
async def delete_item_confirm(
    callback: CallbackQuery,
    callback_data: ItemCB,
    session: AsyncSession,
) -> None:
    """Запросить подтверждение удаления."""
    item = await get_item_by_id(session, callback_data.id)
    if not item:
        await callback.answer("Элемент не найден", show_alert=True)
        return

    await callback.message.edit_text(
        f"🗑 Удалить «<b>{item.title}</b>»?",
        reply_markup=confirm_delete_keyboard(item.id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(ConfirmCB.filter(F.action == "delete_yes"))
async def delete_confirmed(
    callback: CallbackQuery,
    callback_data: ConfirmCB,
    session: AsyncSession,
) -> None:
    """Подтверждённое удаление элемента."""
    item = await get_item_by_id(session, callback_data.item_id)
    if not item:
        await callback.answer("Элемент не найден", show_alert=True)
        return

    title = item.title
    await delete_item(session, item)
    await callback.message.edit_text(
        texts.ITEM_DELETED.format(title=title),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(ConfirmCB.filter(F.action == "delete_no"))
async def delete_cancelled(
    callback: CallbackQuery,
    callback_data: ConfirmCB,
    session: AsyncSession,
) -> None:
    """Отмена удаления — вернуться к деталям."""
    await _show_item_detail(callback, session, callback_data.item_id)
    await callback.answer()

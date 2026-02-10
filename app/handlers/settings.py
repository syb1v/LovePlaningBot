"""Хендлер настроек — имена, ДР, дата отношений, напоминания, праздники."""

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.couple import get_couple_by_id
from app.db.repositories.holiday import (
    create_holiday,
    delete_holiday,
    get_holiday_by_id,
    get_holidays_by_couple,
    toggle_holiday,
)
from app.db.repositories.user import get_user_by_telegram_id
from app.keyboards.callbacks import HolidayCB, RemindCB, SettingsCB
from app.keyboards.inline import (
    holiday_detail_keyboard,
    holidays_keyboard,
    remind_settings_keyboard,
    settings_keyboard,
)
from app.states.forms import BirthdayForm, HolidayForm, NameForm, RelDateForm
from app.utils import texts

router = Router(name="settings")


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message, session: AsyncSession) -> None:
    """Показать меню настроек."""
    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user or not db_user.couple_id:
        await message.answer(texts.NO_COUPLE, parse_mode="HTML")
        return

    couple = await get_couple_by_id(session, db_user.couple_id)
    partner = None
    if couple:
        for u in couple.users:
            if u.telegram_id != db_user.telegram_id:
                partner = u
                break

    rel_date_str = "не указана"
    days_together = ""
    if couple and couple.relationship_date:
        rel_date_str = couple.relationship_date.strftime("%d.%m.%Y")
        delta = (datetime.now().date() - couple.relationship_date).days
        years = delta // 365
        months = (delta % 365) // 30
        if years:
            days_together = f" ({years} г. {months} мес.)"
        else:
            days_together = f" ({months} мес. {delta % 30} дн.)"

    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"👤 Моё имя: <b>{db_user.name}</b>\n"
        f"🎂 Мой ДР: <b>{db_user.birthday or 'не указан'}</b>\n"
    )

    if partner:
        text += (
            f"\n👤 Партнёр: <b>{partner.name}</b>\n"
            f"🎂 ДР партнёра: <b>{partner.birthday or 'не указан'}</b>\n"
        )

    text += (
        f"\n💕 Начало отношений: <b>{rel_date_str}</b>{days_together}\n"
        f"🔗 Код пары: <code>{couple.invite_code if couple else '—'}</code>"
    )

    await message.answer(text, reply_markup=settings_keyboard(), parse_mode="HTML")


# --- Смена имени ---


@router.callback_query(SettingsCB.filter(F.action == "name"))
async def change_name_start(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Запросить новое имя."""
    await state.set_state(NameForm.waiting_name)
    await callback.message.edit_text(
        "✏️ Введите новое имя для отображения в боте:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(NameForm.waiting_name)
async def change_name_process(
    message: Message, session: AsyncSession, state: FSMContext
) -> None:
    """Сохранить новое имя."""
    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user:
        await state.clear()
        return

    db_user.display_name = message.text.strip()
    await session.commit()
    await state.clear()
    await message.answer(
        f"✅ Имя обновлено: <b>{db_user.display_name}</b>",
        parse_mode="HTML",
    )


# --- ДР партнёра ---


@router.callback_query(SettingsCB.filter(F.action == "birthday"))
async def change_birthday_start(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Запросить дату рождения партнёра."""
    await state.set_state(BirthdayForm.waiting_date)
    await callback.message.edit_text(
        "🎂 Введите дату рождения партнёра (ДД.ММ.ГГГГ):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(BirthdayForm.waiting_date)
async def change_birthday_process(
    message: Message, session: AsyncSession, state: FSMContext
) -> None:
    """Сохранить дату рождения партнёра."""
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y")
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте ДД.ММ.ГГГГ")
        return

    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user or not db_user.couple_id:
        await state.clear()
        return

    # Ищем партнёра
    couple = await get_couple_by_id(session, db_user.couple_id)
    if couple:
        for u in couple.users:
            if u.telegram_id != db_user.telegram_id:
                u.birthday = dt.strftime("%d.%m.%Y")
                await session.commit()
                break

    await state.clear()
    await message.answer(
        f"✅ ДР партнёра сохранён: <b>{dt.strftime('%d.%m.%Y')}</b>",
        parse_mode="HTML",
    )


# --- Дата начала отношений ---


@router.callback_query(SettingsCB.filter(F.action == "rel_date"))
async def change_rel_date_start(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Запросить дату начала отношений."""
    await state.set_state(RelDateForm.waiting_date)
    await callback.message.edit_text(
        "💕 Введите дату начала ваших отношений (ДД.ММ.ГГГГ):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(RelDateForm.waiting_date)
async def change_rel_date_process(
    message: Message, session: AsyncSession, state: FSMContext
) -> None:
    """Сохранить дату начала отношений."""
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте ДД.ММ.ГГГГ")
        return

    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user or not db_user.couple_id:
        await state.clear()
        return

    couple = await get_couple_by_id(session, db_user.couple_id)
    if couple:
        couple.relationship_date = dt
        await session.commit()

    await state.clear()
    await message.answer(
        f"✅ Дата отношений сохранена: <b>{dt.strftime('%d.%m.%Y')}</b> 💕",
        parse_mode="HTML",
    )


# --- Настройки напоминаний ---


@router.callback_query(SettingsCB.filter(F.action == "remind"))
async def show_remind_settings(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Показать настройки напоминаний."""
    db_user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not db_user or not db_user.couple_id:
        await callback.answer(texts.NO_COUPLE, show_alert=True)
        return

    couple = await get_couple_by_id(session, db_user.couple_id)
    if not couple:
        return

    await callback.message.edit_text(
        "🔔 <b>Настройки напоминаний</b>\n\n"
        "Выберите, когда получать напоминания о праздниках и годовщинах:",
        reply_markup=remind_settings_keyboard(couple.remind_before),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(RemindCB.filter())
async def toggle_remind(
    callback: CallbackQuery,
    callback_data: RemindCB,
    session: AsyncSession,
) -> None:
    """Переключить флаг напоминания."""
    flag = callback_data.flag

    db_user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not db_user or not db_user.couple_id:
        return

    couple = await get_couple_by_id(session, db_user.couple_id)
    if not couple:
        return

    # Переключаем бит
    couple.remind_before ^= flag
    await session.commit()

    await callback.message.edit_reply_markup(
        reply_markup=remind_settings_keyboard(couple.remind_before),
    )
    await callback.answer()


# --- Праздники ---


@router.callback_query(SettingsCB.filter(F.action == "holidays"))
async def show_holidays(
    callback: CallbackQuery, session: AsyncSession
) -> None:
    """Показать список праздников."""
    db_user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not db_user or not db_user.couple_id:
        await callback.answer(texts.NO_COUPLE, show_alert=True)
        return

    holidays = await get_holidays_by_couple(session, db_user.couple_id)

    text = "🎉 <b>Праздники</b>\n\n"
    if not holidays:
        text += "Пока нет праздников. Добавьте первый!"
    else:
        text += f"Всего: {len(holidays)}"

    await callback.message.edit_text(
        text,
        reply_markup=holidays_keyboard(holidays, db_user.couple_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(HolidayCB.filter(F.action == "view"))
async def view_holiday(
    callback: CallbackQuery,
    callback_data: HolidayCB,
    session: AsyncSession,
) -> None:
    """Показать детали праздника."""
    holiday = await get_holiday_by_id(session, callback_data.id)
    if not holiday:
        await callback.answer("Праздник не найден", show_alert=True)
        return

    status = "✅ Активен" if holiday.is_active else "❌ Выключен"
    remind_parts = []
    if holiday.remind_before & 1:
        remind_parts.append("в день")
    if holiday.remind_before & 2:
        remind_parts.append("за день")
    if holiday.remind_before & 4:
        remind_parts.append("за 3 дня")
    if holiday.remind_before & 8:
        remind_parts.append("за неделю")

    text = (
        f"🎉 <b>{holiday.name}</b>\n\n"
        f"📅 Дата: {holiday.day:02d}.{holiday.month:02d}"
        f"{f'.{holiday.year}' if holiday.year else ' (ежегодно)'}\n"
        f"📌 Статус: {status}\n"
        f"🔔 Напоминания: {', '.join(remind_parts) or 'не настроены'}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=holiday_detail_keyboard(holiday.id, holiday.is_active),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(HolidayCB.filter(F.action == "toggle"))
async def toggle_holiday_handler(
    callback: CallbackQuery,
    callback_data: HolidayCB,
    session: AsyncSession,
) -> None:
    """Включить/выключить праздник."""
    holiday = await get_holiday_by_id(session, callback_data.id)
    if not holiday:
        await callback.answer("Праздник не найден", show_alert=True)
        return

    holiday = await toggle_holiday(session, holiday)
    status = "включён ✅" if holiday.is_active else "выключен ❌"
    await callback.answer(f"Праздник {status}")

    # Обновляем кнопки
    await callback.message.edit_reply_markup(
        reply_markup=holiday_detail_keyboard(holiday.id, holiday.is_active),
    )


@router.callback_query(HolidayCB.filter(F.action == "delete"))
async def delete_holiday_handler(
    callback: CallbackQuery,
    callback_data: HolidayCB,
    session: AsyncSession,
) -> None:
    """Удалить праздник."""
    holiday = await get_holiday_by_id(session, callback_data.id)
    if not holiday:
        await callback.answer("Праздник не найден", show_alert=True)
        return

    name = holiday.name
    await delete_holiday(session, holiday)
    await callback.message.edit_text(
        f"🗑 Праздник «{name}» удалён.",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(HolidayCB.filter(F.action == "add"))
async def add_holiday_start(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Начать добавление праздника."""
    await state.set_state(HolidayForm.waiting_name)
    await callback.message.edit_text(
        "🎉 Введите название праздника:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(HolidayForm.waiting_name)
async def add_holiday_name(
    message: Message, state: FSMContext
) -> None:
    """Получить название праздника."""
    await state.update_data(holiday_name=message.text.strip())
    await state.set_state(HolidayForm.waiting_date)
    await message.answer(
        "📅 Введите дату праздника (ДД.ММ):",
        parse_mode="HTML",
    )


@router.message(HolidayForm.waiting_date)
async def add_holiday_date(
    message: Message, session: AsyncSession, state: FSMContext
) -> None:
    """Создать праздник."""
    text = message.text.strip()

    try:
        parts = text.split(".")
        day = int(parts[0])
        month = int(parts[1])
        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError
    except (ValueError, IndexError):
        await message.answer("❌ Неверный формат. Используйте ДД.ММ")
        return

    data = await state.get_data()
    db_user = await get_user_by_telegram_id(session, message.from_user.id)
    if not db_user or not db_user.couple_id:
        await state.clear()
        return

    holiday = await create_holiday(
        session,
        name=data["holiday_name"],
        month=month,
        day=day,
        couple_id=db_user.couple_id,
    )

    await state.clear()
    await message.answer(
        f"✅ Праздник «<b>{holiday.name}</b>» добавлен на {day:02d}.{month:02d}!",
        parse_mode="HTML",
    )

"""Хендлер /start — регистрация, ввод имени/ДР и привязка к паре."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.couple import create_couple, get_couple_by_invite_code
from app.db.repositories.user import (
    create_user,
    get_user_by_telegram_id,
    update_user_couple,
)
from app.db.seed import seed_couple_data
from app.keyboards.reply import main_menu_keyboard
from app.states.forms import CoupleForm, RegistrationForm
from app.utils import texts

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
    message: Message, session: AsyncSession, state: FSMContext
) -> None:
    """Обработка команды /start — регистрация и выбор действия."""
    await state.clear()

    tg_user = message.from_user
    db_user = await get_user_by_telegram_id(session, tg_user.id)

    # Если уже зарегистрирован и в паре — показываем меню
    if db_user and db_user.couple_id is not None:
        await message.answer(
            texts.WELCOME.format(name=db_user.name),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    # Если уже зарегистрирован, но без пары
    if db_user:
        await _show_couple_choice(message, db_user.name)
        return

    # Новый пользователь — запрашиваем имя
    await state.set_state(RegistrationForm.waiting_name)
    await message.answer(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Как тебя зовут? Введи своё имя:",
        parse_mode="HTML",
    )


@router.message(RegistrationForm.waiting_name)
async def reg_name(
    message: Message, state: FSMContext
) -> None:
    """Получить имя и спросить ДР."""
    name = message.text.strip()
    if len(name) < 1 or len(name) > 64:
        await message.answer("❌ Имя должно быть от 1 до 64 символов.")
        return

    await state.update_data(reg_name=name)
    await state.set_state(RegistrationForm.waiting_birthday)
    await message.answer(
        f"Отлично, <b>{name}</b>! 🎉\n\n"
        "Введи свою дату рождения (ДД.ММ.ГГГГ)\n"
        "или отправь <b>-</b> чтобы пропустить:",
        parse_mode="HTML",
    )


@router.message(RegistrationForm.waiting_birthday)
async def reg_birthday(
    message: Message, session: AsyncSession, state: FSMContext
) -> None:
    """Получить ДР и создать пользователя."""
    text = message.text.strip()
    birthday = None

    if text not in ("-", "нет", "пропустить"):
        from datetime import datetime

        try:
            dt = datetime.strptime(text, "%d.%m.%Y")
            birthday = dt.strftime("%d.%m.%Y")
        except ValueError:
            await message.answer(
                "❌ Неверный формат. Используй <b>ДД.ММ.ГГГГ</b>"
                " или <b>-</b> чтобы пропустить:",
                parse_mode="HTML",
            )
            return

    data = await state.get_data()
    tg_user = message.from_user

    db_user = await create_user(
        session,
        telegram_id=tg_user.id,
        first_name=tg_user.first_name,
        username=tg_user.username,
    )

    # Сохраняем имя и ДР
    db_user.display_name = data["reg_name"]
    if birthday:
        db_user.birthday = birthday
    await session.commit()

    await state.clear()
    await _show_couple_choice(message, db_user.name)


async def _show_couple_choice(message: Message, name: str) -> None:
    """Показать выбор: создать пару или присоединиться."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🆕 Создать пару",
                    callback_data="couple_create",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔗 У меня есть код",
                    callback_data="couple_join",
                ),
            ],
        ]
    )

    await message.answer(
        texts.WELCOME.format(name=name),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "couple_create")
async def create_couple_handler(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Создать новую пару и сгенерировать invite-код."""
    tg_user = callback.from_user
    db_user = await get_user_by_telegram_id(session, tg_user.id)

    if db_user and db_user.couple_id:
        await callback.answer(texts.ALREADY_IN_COUPLE, show_alert=True)
        return

    couple = await create_couple(session)
    await update_user_couple(session, db_user, couple.id)
    await seed_couple_data(session, couple.id, tg_user.id)

    await callback.message.edit_text(
        texts.CREATE_COUPLE.format(code=couple.invite_code),
        parse_mode="HTML",
    )

    await callback.message.answer(
        texts.MENU,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "couple_join")
async def join_couple_prompt(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Запросить invite-код для присоединения к паре."""
    await callback.message.edit_text(
        texts.ENTER_INVITE_CODE,
        parse_mode="HTML",
    )
    await state.set_state(CoupleForm.waiting_invite_code)
    await callback.answer()


@router.message(CoupleForm.waiting_invite_code)
async def process_invite_code(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    """Обработать введённый invite-код."""
    code = message.text.strip()
    couple = await get_couple_by_invite_code(session, code)

    if couple is None or len(couple.users) >= 2:
        await message.answer(texts.INVALID_CODE, parse_mode="HTML")
        return

    tg_user = message.from_user
    db_user = await get_user_by_telegram_id(session, tg_user.id)

    await update_user_couple(session, db_user, couple.id)
    await state.clear()

    await message.answer(
        texts.COUPLE_JOINED,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )

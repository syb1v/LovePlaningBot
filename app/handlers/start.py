"""Хендлер /start — регистрация и привязка к паре."""

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
from app.states.forms import CoupleForm
from app.utils import texts

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext) -> None:
    """Обработка команды /start — регистрация и выбор действия."""
    await state.clear()

    tg_user = message.from_user
    db_user = await get_user_by_telegram_id(session, tg_user.id)

    # Регистрация нового пользователя
    if db_user is None:
        db_user = await create_user(
            session,
            telegram_id=tg_user.id,
            first_name=tg_user.first_name,
            username=tg_user.username,
        )

    # Если уже в паре — показываем меню
    if db_user.couple_id is not None:
        await message.answer(
            texts.WELCOME.format(name=tg_user.first_name),
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
        return

    # Предлагаем создать пару или присоединиться
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🆕 Создать пару", callback_data="couple_create"),
        ],
        [
            InlineKeyboardButton(text="🔗 У меня есть код", callback_data="couple_join"),
        ],
    ])

    await message.answer(
        texts.WELCOME.format(name=tg_user.first_name),
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

    # Создаём пару
    couple = await create_couple(session)

    # Привязываем пользователя
    await update_user_couple(session, db_user, couple.id)

    # Загружаем начальные данные
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

    # Проверяем валидность кода и что пара не заполнена
    if couple is None or len(couple.users) >= 2:
        await message.answer(texts.INVALID_CODE, parse_mode="HTML")
        return

    tg_user = message.from_user
    db_user = await get_user_by_telegram_id(session, tg_user.id)

    # Привязываем к паре
    await update_user_couple(session, db_user, couple.id)

    await state.clear()

    await message.answer(
        texts.COUPLE_JOINED,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )

"""Middleware авторизации — проверка регистрации и привязки к паре."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.db.engine import async_session
from app.db.repositories.user import get_user_by_telegram_id


class AuthMiddleware(BaseMiddleware):
    """Загружает пользователя из БД и кладёт в data['db_user']."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Загрузить пользователя перед обработкой."""
        # Работаем только с Message и CallbackQuery
        user_tg = data.get("event_from_user")
        if user_tg is None:
            return await handler(event, data)

        session = data.get("session")

        # Если сессия уже в data — используем её
        if session:
            db_user = await get_user_by_telegram_id(session, user_tg.id)
            data["db_user"] = db_user
        else:
            async with async_session() as session:
                db_user = await get_user_by_telegram_id(session, user_tg.id)
                data["db_user"] = db_user

        return await handler(event, data)

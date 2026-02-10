"""Middleware для инъекции AsyncSession в каждый хендлер."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.db.engine import async_session


class DbSessionMiddleware(BaseMiddleware):
    """Создаёт AsyncSession и передаёт её в data['session']."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Обернуть хендлер в контекст БД-сессии."""
        async with async_session() as session:
            data["session"] = session
            return await handler(event, data)

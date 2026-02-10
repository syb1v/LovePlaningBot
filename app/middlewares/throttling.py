"""Middleware для ограничения частоты запросов (антиспам)."""

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

# Минимальный интервал между сообщениями (секунды)
THROTTLE_RATE = 0.5


class ThrottlingMiddleware(BaseMiddleware):
    """Ограничивает частоту обработки событий от одного пользователя."""

    def __init__(self) -> None:
        self._last_call: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Пропустить событие, если прошло слишком мало времени."""
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self._last_call.get(user.id, 0.0)

        if now - last < THROTTLE_RATE:
            return None  # игнорируем слишком частые запросы

        self._last_call[user.id] = now
        return await handler(event, data)

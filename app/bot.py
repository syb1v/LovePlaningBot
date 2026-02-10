"""Создание и конфигурация бота и диспетчера."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.handlers import (
    back_nav,
    categories,
    items,
    menu,
    random_pick,
    reminders,
    start,
    stats,
    voting,
)
from app.handlers import (
    settings as settings_handler,
)
from app.middlewares.auth import AuthMiddleware
from app.middlewares.db_session import DbSessionMiddleware
from app.middlewares.throttling import ThrottlingMiddleware

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    """Создать экземпляр бота."""
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Создать и настроить диспетчер с роутерами и middleware."""
    dp = Dispatcher(storage=MemoryStorage())

    # --- Middleware (порядок имеет значение) ---
    dp.update.middleware(ThrottlingMiddleware())
    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(AuthMiddleware())

    # --- Подключение роутеров ---
    dp.include_routers(
        start.router,
        menu.router,
        back_nav.router,
        categories.router,
        items.router,
        voting.router,
        random_pick.router,
        stats.router,
        reminders.router,
        settings_handler.router,
    )

    logger.info("Диспетчер настроен: %d роутеров подключено.", 10)
    return dp

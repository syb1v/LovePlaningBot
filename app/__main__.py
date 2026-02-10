"""Точка входа — запуск бота: python -m app."""

import asyncio
import logging
import sys

from app.bot import create_bot, create_dispatcher
from app.db.engine import init_db
from app.services.scheduler import setup_scheduler


async def main() -> None:
    """Инициализация и запуск бота."""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger(__name__)

    logger.info("🚀 Запуск бота-планировщика для пары...")

    # Инициализация базы данных
    await init_db()
    logger.info("✅ База данных инициализирована.")

    # Создание бота и диспетчера
    bot = create_bot()
    dp = create_dispatcher()

    # Запуск планировщика напоминаний
    setup_scheduler(bot)
    logger.info("⏰ Планировщик напоминаний запущен.")

    # Запуск polling
    logger.info("🤖 Бот запущен и слушает обновления...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

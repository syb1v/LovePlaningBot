"""Конфигурация приложения — чтение переменных окружения через pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Настройки бота, загружаемые из .env файла."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )

    # Токен Telegram-бота
    bot_token: str

    # URL подключения к базе данных
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'planner.db'}"


# Глобальный экземпляр настроек
settings = Settings()

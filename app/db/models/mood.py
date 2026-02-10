"""Модель настроения — ежедневный эмодзи-статус."""

from datetime import date as date_type

from sqlalchemy import BigInteger, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Mood(Base):
    """Настроение пользователя на определённый день."""

    __tablename__ = "moods"

    # Кто поставил настроение (telegram_id)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Привязка к паре
    couple_id: Mapped[int] = mapped_column(
        ForeignKey("couples.id"), nullable=False
    )

    # Эмодзи настроения
    emoji: Mapped[str] = mapped_column(String(8), nullable=False)

    # Дата
    date: Mapped[date_type] = mapped_column(Date, nullable=False)

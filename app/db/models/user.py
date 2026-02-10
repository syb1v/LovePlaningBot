"""Модель пользователя Telegram."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.couple import Couple


class User(Base):
    """Пользователь Telegram, привязанный к паре."""

    __tablename__ = "users"

    # Telegram user ID (уникальный)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )

    # Имя пользователя в Telegram
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Имя (first_name из Telegram)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)

    # Кастомное имя для отображения в боте
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Дата рождения (для напоминаний)
    birthday: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Привязка к паре (может быть NULL, если ещё не в паре)
    couple_id: Mapped[int | None] = mapped_column(
        ForeignKey("couples.id"), nullable=True
    )

    couple: Mapped[Couple | None] = relationship(
        "Couple", back_populates="users", lazy="selectin"
    )

    @property
    def name(self) -> str:
        """Отображаемое имя (кастомное или из Telegram)."""
        return self.display_name or self.first_name

"""Модель пары — связывает двух пользователей."""

from __future__ import annotations

from datetime import date  # noqa: TCH003 — must be runtime for SQLAlchemy Mapped
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class Couple(Base):
    """Пара пользователей с общим пространством планирования."""

    __tablename__ = "couples"

    # Уникальный код-приглашение для присоединения партнёра
    invite_code: Mapped[str] = mapped_column(
        String(16), unique=True, nullable=False
    )

    # Дата начала отношений
    relationship_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Настройки напоминаний о годовщинах
    remind_monthly: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    remind_yearly: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    # За сколько дней напоминать (битовые флаги: 1=в день, 2=за день, 4=за 3 дня, 8=за неделю)
    remind_before: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3  # по умолчанию: в день + за день
    )

    # Связанные пользователи (макс. 2)
    users: Mapped[list[User]] = relationship(
        "User", back_populates="couple", lazy="selectin"
    )

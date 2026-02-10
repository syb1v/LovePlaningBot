"""Модель элемента плана — сериал, фильм, игра, дело или цель."""

from __future__ import annotations

import enum
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.category import Category


class ItemStatus(enum.StrEnum):
    """Статус элемента планирования."""

    PENDING = "pending"          # ожидает
    IN_PROGRESS = "in_progress"  # в процессе
    DONE = "done"                # завершён


class PlanItem(Base):
    """Элемент совместного плана (фильм, сериал, задача и т.д.)."""

    __tablename__ = "plan_items"

    # Название
    title: Mapped[str] = mapped_column(String(256), nullable=False)

    # Текущий статус
    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus), nullable=False, default=ItemStatus.PENDING
    )

    # Приоритет (1 — высший)
    priority: Mapped[int] = mapped_column(nullable=False, default=3)

    # Дедлайн (опционально)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Заметки
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Кто добавил (telegram_id)
    added_by_id: Mapped[int] = mapped_column(nullable=False)

    # Привязка к категории
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )

    category: Mapped[Category] = relationship(
        "Category", back_populates="items", lazy="selectin"
    )

    # Привязка к паре
    couple_id: Mapped[int] = mapped_column(
        ForeignKey("couples.id"), nullable=False
    )

    # Ожидает подтверждения партнёром (wishlist-режим)
    is_wishlist: Mapped[bool] = mapped_column(nullable=False, default=False)

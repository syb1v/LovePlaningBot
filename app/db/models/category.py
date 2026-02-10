"""Модель категории — группировка элементов планирования."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.item import PlanItem


class Category(Base):
    """Категория элементов (сериалы, фильмы, игры, дела, цели)."""

    __tablename__ = "categories"

    # Название категории
    name: Mapped[str] = mapped_column(String(64), nullable=False)

    # Иконка-эмодзи
    icon: Mapped[str] = mapped_column(String(4), nullable=False, default="📋")

    # Привязка к паре
    couple_id: Mapped[int] = mapped_column(
        ForeignKey("couples.id"), nullable=False
    )

    # Элементы в категории
    items: Mapped[list[PlanItem]] = relationship(
        "PlanItem", back_populates="category", lazy="selectin",
        cascade="all, delete-orphan",
    )

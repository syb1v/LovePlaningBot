"""Модель праздника — управляемые даты событий для пары."""


from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Holiday(Base):
    """Праздник или важная дата для пары."""

    __tablename__ = "holidays"

    # Название праздника
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    # День и месяц (ежегодные) — формат: MM-DD
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)

    # Год (опционально, для одноразовых событий)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Привязка к паре
    couple_id: Mapped[int] = mapped_column(
        ForeignKey("couples.id"), nullable=False
    )

    # Настройки напоминаний (битовые флаги: 1=в день, 2=за день, 4=за 3 дня, 8=за неделю)
    remind_before: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3  # в день + за день
    )

    # Активен ли праздник
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

"""Модель голосования — подтверждение/отклонение предложений."""

from sqlalchemy import BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Vote(Base):
    """Голос пользователя за/против предложенного элемента."""

    __tablename__ = "votes"

    # Элемент, за который голосуют
    item_id: Mapped[int] = mapped_column(
        ForeignKey("plan_items.id", ondelete="CASCADE"), nullable=False
    )

    # Кто голосует (telegram_id)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Одобрено или отклонено
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)

"""Репозиторий элементов плана — CRUD-операции для модели PlanItem."""

import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.item import ItemStatus, PlanItem


async def get_items_by_category(
    session: AsyncSession,
    category_id: int,
) -> list[PlanItem]:
    """Получить все элементы категории."""
    stmt = (
        select(PlanItem)
        .where(PlanItem.category_id == category_id)
        .order_by(PlanItem.priority, PlanItem.id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_items_by_couple(
    session: AsyncSession,
    couple_id: int,
    status: ItemStatus | None = None,
) -> list[PlanItem]:
    """Получить все элементы пары (опционально по статусу)."""
    stmt = select(PlanItem).where(PlanItem.couple_id == couple_id)
    if status is not None:
        stmt = stmt.where(PlanItem.status == status)
    stmt = stmt.order_by(PlanItem.priority, PlanItem.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_item_by_id(
    session: AsyncSession,
    item_id: int,
) -> PlanItem | None:
    """Получить элемент по ID."""
    stmt = select(PlanItem).where(PlanItem.id == item_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_item(
    session: AsyncSession,
    title: str,
    category_id: int,
    couple_id: int,
    added_by_id: int,
    deadline: str | None = None,
    priority: int = 3,
    notes: str | None = None,
    is_wishlist: bool = False,
) -> PlanItem:
    """Создать новый элемент плана."""
    item = PlanItem(
        title=title,
        category_id=category_id,
        couple_id=couple_id,
        added_by_id=added_by_id,
        deadline=deadline,
        priority=priority,
        notes=notes,
        is_wishlist=is_wishlist,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def update_item_status(
    session: AsyncSession,
    item: PlanItem,
    status: ItemStatus,
) -> PlanItem:
    """Обновить статус элемента."""
    item.status = status
    await session.commit()
    await session.refresh(item)
    return item


async def delete_item(session: AsyncSession, item: PlanItem) -> None:
    """Удалить элемент."""
    await session.delete(item)
    await session.commit()


async def get_random_pending_item(
    session: AsyncSession,
    couple_id: int,
    category_id: int | None = None,
) -> PlanItem | None:
    """Получить случайный незавершённый элемент."""
    stmt = select(PlanItem).where(
        PlanItem.couple_id == couple_id,
        PlanItem.status != ItemStatus.DONE,
        PlanItem.is_wishlist.is_(False),
    )
    if category_id is not None:
        stmt = stmt.where(PlanItem.category_id == category_id)

    result = await session.execute(stmt)
    items = list(result.scalars().all())
    return random.choice(items) if items else None


async def get_wishlist_items(
    session: AsyncSession,
    couple_id: int,
) -> list[PlanItem]:
    """Получить все элементы в wishlist (ожидающие подтверждения)."""
    stmt = (
        select(PlanItem)
        .where(
            PlanItem.couple_id == couple_id,
            PlanItem.is_wishlist.is_(True),
        )
        .order_by(PlanItem.id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def approve_wishlist_item(
    session: AsyncSession,
    item: PlanItem,
) -> PlanItem:
    """Одобрить элемент из wishlist — перевести в обычные элементы."""
    item.is_wishlist = False
    await session.commit()
    await session.refresh(item)
    return item


async def get_items_with_deadline(
    session: AsyncSession,
    couple_id: int,
) -> list[PlanItem]:
    """Получить все элементы с дедлайнами (незавершённые)."""
    stmt = (
        select(PlanItem)
        .where(
            PlanItem.couple_id == couple_id,
            PlanItem.deadline.isnot(None),
            PlanItem.status != ItemStatus.DONE,
        )
        .order_by(PlanItem.deadline)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())

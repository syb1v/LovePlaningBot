"""Репозиторий категорий — CRUD-операции для модели Category."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.category import Category


async def get_categories_by_couple(
    session: AsyncSession,
    couple_id: int,
) -> list[Category]:
    """Получить все категории пары."""
    stmt = (
        select(Category)
        .options(selectinload(Category.items))
        .where(Category.couple_id == couple_id)
        .order_by(Category.id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_category_by_id(
    session: AsyncSession,
    category_id: int,
) -> Category | None:
    """Получить категорию по ID."""
    stmt = (
        select(Category)
        .options(selectinload(Category.items))
        .where(Category.id == category_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_category(
    session: AsyncSession,
    name: str,
    icon: str,
    couple_id: int,
) -> Category:
    """Создать новую категорию."""
    category = Category(name=name, icon=icon, couple_id=couple_id)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category

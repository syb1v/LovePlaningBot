"""Seed-данные — начальные категории и элементы для новой пары."""

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.category import Category
from app.db.models.item import PlanItem

# Начальные категории с иконками
SEED_CATEGORIES: list[dict[str, str]] = [
    {"name": "Сериалы", "icon": "📺"},
    {"name": "Фильмы", "icon": "🍿"},
    {"name": "Игры", "icon": "🎮"},
    {"name": "Дела", "icon": "✅"},
    {"name": "Цели", "icon": "🎯"},
]

# Начальные элементы (индекс — порядковый номер категории)
SEED_ITEMS: dict[int, list[dict]] = {
    0: [  # Сериалы
        {"title": "Бесстыжие"},
        {"title": "Игра престолов"},
        {"title": "Отчаянные домохозяйки"},
        {"title": "Эйфория"},
        {"title": "Во все тяжкие"},
        {"title": "Очень странные дела"},
    ],
    1: [  # Фильмы
        {"title": "Духлесс 1"},
        {"title": "Духлесс 2"},
        {"title": "Оппенгеймер"},
        {"title": "Легенда"},
        {"title": "Вечность"},
        {"title": "Наполеон"},
        {"title": "По соображениям совести"},
        {"title": "Под покровом ночи"},
    ],
    2: [  # Игры
        {"title": "Детроит: Стать человеком"},
        {"title": "Зайчик"},
    ],
    3: [  # Дела
        {"title": "Написать номер Виты на месте моего в прогрессе"},
    ],
    4: [  # Цели
        {"title": "Съездить на море отдохнуть", "deadline": date(2026, 7, 1)},
        {"title": "Съехаться", "deadline": date(2027, 7, 1)},
    ],
}


async def seed_couple_data(
    session: AsyncSession,
    couple_id: int,
    added_by_id: int,
) -> None:
    """Заполнить начальные данные для новой пары."""
    categories: list[Category] = []

    # Создаём категории
    for cat_data in SEED_CATEGORIES:
        category = Category(
            name=cat_data["name"],
            icon=cat_data["icon"],
            couple_id=couple_id,
        )
        session.add(category)
        categories.append(category)

    await session.flush()  # Получаем ID категорий

    # Создаём элементы
    for cat_index, items_data in SEED_ITEMS.items():
        category = categories[cat_index]
        for item_data in items_data:
            item = PlanItem(
                title=item_data["title"],
                category_id=category.id,
                couple_id=couple_id,
                added_by_id=added_by_id,
                deadline=item_data.get("deadline"),
            )
            session.add(item)

    await session.commit()

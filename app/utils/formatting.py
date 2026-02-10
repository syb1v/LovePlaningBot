"""Форматирование сообщений бота."""

from app.db.models.category import Category
from app.db.models.item import ItemStatus
from app.utils.helpers import progress_bar


def format_category_progress(categories: list[Category]) -> str:
    """Сформировать прогресс по всем категориям."""
    lines = []
    for cat in categories:
        total = len(cat.items)
        done = sum(1 for item in cat.items if item.status == ItemStatus.DONE)
        bar = progress_bar(done, total)
        lines.append(f"{cat.icon} {cat.name}: {bar} {done}/{total}")
    return "\n".join(lines)


def format_items_count(categories: list[Category]) -> tuple[int, int]:
    """Подсчитать общее количество элементов и завершённых."""
    total = sum(len(cat.items) for cat in categories)
    done = sum(
        sum(1 for item in cat.items if item.status == ItemStatus.DONE)
        for cat in categories
    )
    return total, done

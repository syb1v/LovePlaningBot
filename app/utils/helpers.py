"""Вспомогательные функции."""

from app.db.models.item import ItemStatus

# Читаемые названия статусов
STATUS_LABELS = {
    ItemStatus.PENDING: "⏳ Ожидает",
    ItemStatus.IN_PROGRESS: "🔄 В процессе",
    ItemStatus.DONE: "✅ Готово",
}


def progress_bar(done: int, total: int, length: int = 10) -> str:
    """Создать текстовый прогресс-бар.

    Пример: ████░░░░░░ 4/10
    """
    if total == 0:
        return "░" * length
    filled = round(done / total * length)
    return "█" * filled + "░" * (length - filled)


def format_deadline(deadline) -> str:
    """Отформатировать дедлайн для отображения."""
    if deadline is None:
        return ""
    return f"🗓 Дедлайн: <b>{deadline.strftime('%d.%m.%Y')}</b>\n"


def format_notes(notes: str | None) -> str:
    """Отформатировать заметки для отображения."""
    if not notes:
        return ""
    return f"📝 Заметки: <i>{notes}</i>\n"

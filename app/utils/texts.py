"""Все тексты бота — сосредоточены в одном месте для удобства."""

# --- Приветствие и регистрация ---

WELCOME = (
    "💑 <b>Привет, {name}!</b>\n\n"
    "Я — ваш совместный планировщик для пары.\n"
    "Здесь вы можете вместе планировать фильмы, сериалы, "
    "игры, дела и жизненные цели!\n\n"
    "Выберите действие:"
)

CREATE_COUPLE = (
    "🆕 Ты создал(а) новую пару!\n\n"
    "Отправь этот код своему партнёру:\n"
    "<code>{code}</code>\n\n"
    "Партнёр должен нажать /start и ввести этот код."
)

ENTER_INVITE_CODE = (
    "🔗 Введи invite-код от партнёра, чтобы присоединиться к паре:"
)

COUPLE_JOINED = (
    "🎉 <b>Вы теперь пара!</b>\n\n"
    "Все ваши планы, фильмы, сериалы и цели теперь общие.\n"
    "Начальные данные загружены — можете приступать! 💕"
)

INVALID_CODE = "❌ Неверный код или пара уже заполнена. Попробуй ещё раз:"

ALREADY_IN_COUPLE = "💕 Ты уже состоишь в паре! Используй меню для навигации."

NO_COUPLE = "⚠️ Сначала создай пару или присоединись к существующей (/start)."

# --- Главное меню ---

MENU = "💑 <b>Главное меню</b>\n\nВыбери, что хочешь сделать:"

# --- Категории ---

CATEGORIES_HEADER = "📂 <b>Ваши категории:</b>\n\nВыбери категорию:"

CATEGORY_ITEMS_HEADER = (
    "{icon} <b>{name}</b>\n"
    "Всего: {total} | ✅ {done} | 🔄 {in_progress} | ⏳ {pending}\n\n"
    "Выбери элемент или добавь новый:"
)

EMPTY_CATEGORY = (
    "{icon} <b>{name}</b>\n\n"
    "Пока пусто. Нажми ➕ чтобы добавить!"
)

# --- Элементы ---

ITEM_DETAIL = (
    "📌 <b>{title}</b>\n\n"
    "📂 Категория: {category}\n"
    "📍 Статус: {status}\n"
    "{deadline}"
    "{notes}"
    "\nВыбери действие:"
)

ITEM_ADDED = "✅ <b>{title}</b> добавлен(а) в «{category}»!"
ITEM_STATUS_CHANGED = "📍 Статус «{title}» изменён на: {status}"
ITEM_DELETED = "🗑 «{title}» удалён(а)."
ITEM_DELETE_CANCELLED = "❌ Удаление отменено."

ENTER_ITEM_TITLE = "✏️ Введи название:"
ENTER_DEADLINE = (
    "🗓 Введи дедлайн в формате <b>ДД.ММ.ГГГГ</b>\n"
    "(или отправь <b>нет</b> чтобы убрать):"
)
DEADLINE_SET = "🗓 Дедлайн для «{title}» установлен: <b>{date}</b>"
DEADLINE_REMOVED = "🗓 Дедлайн для «{title}» снят."
INVALID_DATE = "❌ Неверный формат даты. Используй <b>ДД.ММ.ГГГГ</b>:"

ENTER_NOTE = "📝 Введи заметку для «{title}»:"
NOTE_SAVED = "📝 Заметка сохранена!"

# --- Рандом ---

RANDOM_HEADER = "🎲 <b>Случайный выбор</b>\n\nИз какой категории выбрать?"

RANDOM_RESULT = (
    "🎲 <b>Сегодня предлагаю:</b>\n\n"
    "{icon} {title}\n"
    "📂 {category}"
)

RANDOM_EMPTY = "😅 Нет незавершённых элементов для выбора."

# --- Настроение ---

MOOD_HEADER = "💕 <b>Настроение дня</b>\n\nВыбери своё настроение:"

MOOD_SET = (
    "💕 Твоё настроение: {my_mood}\n"
    "{partner_line}"
)

MOOD_PARTNER_LINE = "Настроение партнёра: {partner_mood}"
MOOD_PARTNER_NONE = "Партнёр ещё не выбрал(а) настроение сегодня 🤷"

# --- Статистика ---

STATS_HEADER = (
    "📊 <b>Статистика пары</b>\n\n"
    "👫 Дней в боте: <b>{days}</b>\n"
    "✅ Завершено дел: <b>{done}</b>\n"
    "📋 Всего элементов: <b>{total}</b>\n\n"
    "<b>Прогресс по категориям:</b>\n"
    "{categories_progress}"
)

STATS_CATEGORY_LINE = "{icon} {name}: {bar} {done}/{total}"

# --- Wishlist ---

WISHLIST_HEADER = (
    "💌 <b>Wishlist</b>\n\n"
    "Предложения, ожидающие одобрения партнёра:"
)

WISHLIST_EMPTY = "💌 Wishlist пуст. Предложи что-нибудь партнёру!"

WISHLIST_ITEM = "💌 <b>Предложение:</b> {title}\n📂 {category}\n👤 От: {from_name}"

WISHLIST_APPROVED = "✅ «{title}» одобрено и добавлено в планы!"
WISHLIST_REJECTED = "❌ «{title}» отклонено."

WISHLIST_SENT = "💌 Предложение «{title}» отправлено партнёру на одобрение!"

# --- Настройки ---

SETTINGS_HEADER = (
    "⚙️ <b>Настройки</b>\n\n"
    "🔗 Код вашей пары: <code>{code}</code>\n"
    "👤 Ты: {user_name}\n"
    "💕 Партнёр: {partner_name}"
)

NO_PARTNER_YET = "ещё не присоединился(ась)"

# --- Напоминания ---

REMINDER_DEADLINE = (
    "⏰ <b>Напоминание!</b>\n\n"
    "📌 «{title}» — дедлайн {when}!\n"
    "📂 {category}"
)

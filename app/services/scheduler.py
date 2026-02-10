"""Сервис планировщика напоминаний через APScheduler."""

import logging
from datetime import date
from zoneinfo import ZoneInfo

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.db.engine import async_session
from app.db.models.item import ItemStatus
from app.db.repositories.couple import get_couple_by_id
from app.db.repositories.item import get_items_with_deadline

logger = logging.getLogger(__name__)

# Таймзона Москвы
MSK = ZoneInfo("Europe/Moscow")

# Глобальный экземпляр планировщика
scheduler = AsyncIOScheduler(timezone=MSK)

# Битовые флаги напоминаний
REMIND_ON_DAY = 1
REMIND_1_DAY = 2
REMIND_3_DAYS = 4
REMIND_7_DAYS = 8


def _should_remind(remind_before: int, days_left: int) -> str | None:
    """Проверить, нужно ли напоминать за days_left дней."""
    if days_left == 0 and remind_before & REMIND_ON_DAY:
        return "сегодня 🎉"
    if days_left == 1 and remind_before & REMIND_1_DAY:
        return "завтра"
    if days_left == 3 and remind_before & REMIND_3_DAYS:
        return "через 3 дня"
    if days_left == 7 and remind_before & REMIND_7_DAYS:
        return "через неделю"
    return None


def setup_scheduler(bot: Bot) -> None:
    """Настроить и запустить планировщик напоминаний."""

    async def check_deadlines() -> None:
        """Проверить дедлайны и отправить напоминания."""
        logger.info("Проверка дедлайнов...")
        today = date.today()

        async with async_session() as session:
            from sqlalchemy import distinct, select

            from app.db.models.item import PlanItem

            stmt = select(distinct(PlanItem.couple_id)).where(
                PlanItem.deadline.isnot(None),
                PlanItem.status != ItemStatus.DONE,
            )
            result = await session.execute(stmt)
            couple_ids = [row[0] for row in result.all()]

            for couple_id in couple_ids:
                items = await get_items_with_deadline(session, couple_id)
                couple = await get_couple_by_id(session, couple_id)

                if not couple:
                    continue

                for item in items:
                    days_left = (item.deadline - today).days

                    if days_left in (7, 3, 1, 0):
                        when = _should_remind(couple.remind_before, days_left)
                        if not when:
                            continue

                        cat_name = item.category.name if item.category else "—"
                        for user in couple.users:
                            try:
                                await bot.send_message(
                                    user.telegram_id,
                                    f"⏰ <b>{item.title}</b> — {when}!\n"
                                    f"📂 {cat_name}",
                                    parse_mode="HTML",
                                )
                            except Exception as e:
                                logger.warning(
                                    "Не удалось отправить: user=%s: %s",
                                    user.telegram_id,
                                    e,
                                )

    async def check_holidays() -> None:
        """Проверить праздники и годовщины."""
        logger.info("Проверка праздников и годовщин...")
        today = date.today()

        async with async_session() as session:
            from sqlalchemy import select

            from app.db.models.couple import Couple
            from app.db.models.holiday import Holiday

            # Праздники
            stmt = select(Holiday).where(Holiday.is_active.is_(True))
            result = await session.execute(stmt)
            holidays = result.scalars().all()

            for holiday in holidays:
                # Считаем дни до праздника в этом году
                try:
                    holiday_date = date(today.year, holiday.month, holiday.day)
                except ValueError:
                    continue

                if holiday_date < today:
                    holiday_date = date(today.year + 1, holiday.month, holiday.day)

                days_left = (holiday_date - today).days

                when = _should_remind(holiday.remind_before, days_left)
                if not when:
                    continue

                couple = await get_couple_by_id(session, holiday.couple_id)
                if not couple:
                    continue

                for user in couple.users:
                    try:
                        await bot.send_message(
                            user.telegram_id,
                            f"🎉 <b>{holiday.name}</b> — {when}!",
                            parse_mode="HTML",
                        )
                    except Exception as e:
                        logger.warning("Не удалось отправить: user=%s: %s", user.telegram_id, e)

            # Годовщины отношений
            stmt = select(Couple).where(Couple.relationship_date.isnot(None))
            result = await session.execute(stmt)
            couples = result.scalars().all()

            for couple in couples:
                rel_date = couple.relationship_date
                # Проверяем месячницу (каждый месяц)
                if couple.remind_monthly and rel_date.day == today.day:
                    months = (today.year - rel_date.year) * 12 + (today.month - rel_date.month)
                    if months > 0:
                        word = "месяц" if months == 1 else "месяцев"
                        msg = f"💕 Сегодня <b>{months}</b> {word} вместе! 🥰"
                        for user in couple.users:
                            try:
                                await bot.send_message(
                                    user.telegram_id,
                                    msg,
                                    parse_mode="HTML",
                                )
                            except Exception as e:
                                logger.warning("user=%s: %s", user.telegram_id, e)

                # Годовщина
                is_anniversary = (
                    couple.remind_yearly
                    and rel_date.month == today.month
                    and rel_date.day == today.day
                )
                if is_anniversary:
                    years = today.year - rel_date.year
                    if years > 0:
                        word = "год" if years == 1 else "лет"
                        msg = f"🎊 Сегодня <b>{years}</b> {word} вместе! 💍🥳"
                        for user in couple.users:
                            try:
                                await bot.send_message(
                                    user.telegram_id,
                                    msg,
                                    parse_mode="HTML",
                                )
                            except Exception as e:
                                logger.warning("user=%s: %s", user.telegram_id, e)

    # Ежедневная проверка в 10:00 МСК
    scheduler.add_job(
        check_deadlines,
        "cron",
        hour=10,
        minute=0,
        id="check_deadlines",
        replace_existing=True,
    )

    # Праздники в 09:00 МСК
    scheduler.add_job(
        check_holidays,
        "cron",
        hour=9,
        minute=0,
        id="check_holidays",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Планировщик запущен (МСК): дедлайны 10:00, праздники 09:00")

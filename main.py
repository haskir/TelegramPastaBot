import asyncio
import os
from datetime import UTC, datetime

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from src.di import DIProvider, configure_dishka
from src.routers import configure_admin_router, user_router


def on_startup():
    logger.info(f"Бот запущен: {datetime.now(UTC)}")


def on_shutdown():
    logger.info(f"Бот остановлен: {datetime.now(UTC)}")


def configure_dispatcher() -> Dispatcher:
    storage: MemoryStorage = MemoryStorage()
    dispatcher: Dispatcher = Dispatcher(storage=storage)
    dispatcher.include_router(user_router)
    dispatcher.include_router(configure_admin_router(int(os.getenv("ADMIN_ID"))))
    return dispatcher


def init_scheduler(di_provider: DIProvider, scheduler: AsyncIOScheduler) -> None:
    scheduler.start()
    scheduler.add_job(di_provider.sender.send_to_users, CronTrigger(hour=6, minute=0, timezone=UTC))
    scheduler.add_job(di_provider.pasta_list.update_list_of_pastas, CronTrigger(hour="*"), jitter=120)


async def main():
    dotenv.load_dotenv()

    bot: Bot = Bot(token=os.getenv("BOT_TOKEN"))
    dispatcher: Dispatcher = configure_dispatcher()

    scheduler: AsyncIOScheduler = AsyncIOScheduler()

    provider: DIProvider = await configure_dishka(bot, dispatcher, scheduler)
    init_scheduler(provider, scheduler)

    try:
        await dispatcher.start_polling(
            bot,
            skip_updates=True,
            on_startup=on_startup(),
        )
    except (asyncio.CancelledError, KeyboardInterrupt):
        await bot.session.close()
        on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())

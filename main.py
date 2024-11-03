import asyncio
from datetime import datetime

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Functions import *
from Keyboards import *

scheduler = AsyncIOScheduler()

dotenv.load_dotenv()
API_TOKEN: str = os.getenv('TelegramPastaBot_token')
ADMIN_ID: int = int(os.getenv('ADMIN_ID'))

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN)
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot=bot, storage=storage)
subscribed_users = set()
[subscribed_users.add(user) for user in read_users()]
mailing_enabled = True
goal_time = datetime.strptime('09:00', '%H:%M')


async def send(user: int):
    keyboard = unsubscribe_keyboard if user in subscribed_users else subscribe_keyboard
    asyncio.create_task(
        bot.send_message(
            user,
            text=pasta_to_markdown(await get_pasta()),
            parse_mode="MarkdownV2",
            reply_markup=keyboard.as_markup()
        )
    )


async def send_mailing():
    if not mailing_enabled:
        return
    tasks = {user: asyncio.create_task(send(user)) for user in subscribed_users}
    for user, task in tasks.items():
        try:
            await task
        except TelegramForbiddenError:
            remove_user(user)


@dp.message(Command(commands=['start_mailing']))
async def start_mailing(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer(text="Только админу разрешено.")
        return
    global mailing_enabled
    if mailing_enabled:
        await message.answer(text="Рассылка уже была включена ранее")
        return
    mailing_enabled = True
    await message.answer(text=f"Включил рассылку на {goal_time.time()}")


@dp.message(Command(commands=['stop_mailing']))
async def stop_mailing(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer(text="Только админу разрешено.")
        return
    global mailing_enabled
    if mailing_enabled:
        mailing_enabled = False
        await message.answer(text="Выключил рассылку")
        return
    await message.answer(text="Рассылка неактивна")


@dp.message()
async def Any(message: Message):
    await message.answer(text="Привет, я паста-бот, все пасты я беру с сайта\nhttps://copypastas.ru/\n",
                         reply_markup=subscribe_keyboard.as_markup())


@dp.callback_query(lambda callback: "Subscribe" in callback.data)
async def Subscribe(callback: CallbackQuery):
    user = callback.from_user.id
    if user in subscribed_users:
        return
    await callback.message.answer(text="Буду слать пасту каждый день в 9:00",
                                  reply_markup=unsubscribe_keyboard.as_markup())
    subscribed_users.add(user)
    add_user_to_file(user)


@dp.callback_query(lambda callback: "Unsubscribe" in callback.data)
async def Unsubscribe(callback: CallbackQuery):
    user = callback.from_user.id
    if user not in subscribed_users:
        return
    subscribed_users.remove(user)
    await callback.message.answer(text="Больше не буду слать пасту каждый день",
                                  reply_markup=subscribe_keyboard.as_markup())
    remove_user(user)


@dp.callback_query(lambda callback: "More" in callback.data)
async def More(callback: CallbackQuery):
    await send(callback.from_user.id)


def on_startup():
    scheduler.add_job(pastas_list.update_list_of_pastas, "cron", hour="*", jitter=120)
    scheduler.add_job(send_mailing, "cron", hour=9, jitter=120)
    scheduler.start()


async def main():
    await dp.start_polling(bot, skip_updates=True, on_startup=on_startup())


if __name__ == '__main__':
    asyncio.run(main())

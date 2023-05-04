import asyncio, dotenv, datetime, os
from asyncio import sleep as asleep
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from Functions import get_pasta, add_user, remove_user, read_users, update_list
from Keyboards import *

dotenv.load_dotenv()

API_TOKEN: str = os.getenv('BOT_TOKEN')
ADMIN_ID: int = int(os.getenv('ADMIN_ID'))

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN)
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot=bot, storage=storage)
subscribed_users = set()
[subscribed_users.add(user) for user in read_users()]
mailing_enabled = False


@dp.message(Command(commands=['start_mailing']))
async def start_mailing(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer(text="Только админу разрешено.")
        return
    global mailing_enabled
    if mailing_enabled:
        await message.answer(text="Рассылка уже было включена ранее")
        return
    mailing_enabled = True
    await message.answer(text="Включил рассылку")
    if datetime.datetime.now().hour == 9:
        update_list()
        for user in subscribed_users:
            await bot.send_message(int(user), get_pasta(), reply_markup=unsubscribe_keyboard.as_markup())
            await asleep(3600 * 24)
    else:
        if datetime.datetime.now().minute == 0:
            await asleep(3600)
            await start_mailing(message)
        else:
            await asleep((60 - datetime.datetime.now().minute) * 60)
            await start_mailing(message)


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
    await callback.message.answer(text="Буду слать пасту каждый день в 9:00",
                                  reply_markup=unsubscribe_keyboard.as_markup())
    user = str(callback.from_user.id)
    subscribed_users.add(user)
    add_user(user)


@dp.callback_query(lambda callback: "Unsubscribe" in callback.data)
async def Unbscribe(callback: CallbackQuery):
    await callback.message.answer(text="Больше не буду слать пасту каждый день",
                                  reply_markup=subscribe_keyboard.as_markup())
    user = str(callback.from_user.id)
    subscribed_users.remove(user)
    remove_user(user)


@dp.callback_query(lambda callback: "More" in callback.data)
async def More(callback: CallbackQuery):
    keyboard = subscribe_keyboard if str(callback.from_user.id) not in subscribed_users else unsubscribe_keyboard
    await callback.message.answer(text=get_pasta(),
                                  reply_markup=keyboard.as_markup())


async def main():
    await dp.start_polling(bot)


# Запускаем бота
if __name__ == '__main__':
    asyncio.run(main())

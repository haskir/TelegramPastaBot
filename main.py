import asyncio, dotenv, os, time
from asyncio import sleep as asleep
import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from Functions import get_pasta, add_user_to_file, remove_user, read_users, update_list
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
goal_time = datetime.datetime.strptime('09:00', '%H:%M')


async def send_mailing():
    if not mailing_enabled:
        return
    if datetime.datetime.now().hour == goal_time.hour and datetime.datetime.now().minute == goal_time.minute:
        update_list()
        for user in subscribed_users:
            await bot.send_message(int(user), get_pasta(), reply_markup=unsubscribe_keyboard.as_markup())
        print(f"{datetime.datetime.now()}\n"
              f"Отправил рассылку {len(subscribed_users)}пользователям, теперь жду 24 часа")
        await asleep(60 * 60 * 24 - 1)
    else:
        await asleep((goal_time - datetime.datetime.now()).seconds + 1)
        await send_mailing()


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
    await send_mailing()


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
    user = str(callback.from_user.id)
    if user in subscribed_users:
        return
    await callback.message.answer(text="Буду слать пасту каждый день в 9:00",
                                  reply_markup=unsubscribe_keyboard.as_markup())
    subscribed_users.add(user)
    add_user_to_file(user)


@dp.callback_query(lambda callback: "Unsubscribe" in callback.data)
async def Unbscribe(callback: CallbackQuery):
    user = str(callback.from_user.id)
    if user not in subscribed_users:
        return
    subscribed_users.remove(user)
    await callback.message.answer(text="Больше не буду слать пасту каждый день",
                                  reply_markup=subscribe_keyboard.as_markup())
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

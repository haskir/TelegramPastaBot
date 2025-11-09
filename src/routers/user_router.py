from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from src.helpers import ScheduleSender, subscribe_keyboard, unsubscribe_keyboard

__all__ = ["user_router"]


user_router = Router(name="User router")


@user_router.message()
async def any_message_handler(message: Message):
    await message.answer(
        text="Привет, я паста-бот, все пасты я беру с сайта\nhttps://copypastas.ru/\n",
        reply_markup=subscribe_keyboard.as_markup(),
    )


@user_router.callback_query(lambda callback: "Subscribe" in callback.data)
async def subscribe(callback: CallbackQuery, sender: FromDishka[ScheduleSender]):
    user: int = callback.from_user.id
    await callback.message.answer(
        text="Буду слать пасту каждый день в 9:00",
        reply_markup=unsubscribe_keyboard.as_markup(),
    )
    with suppress(TelegramAPIError):
        await callback.answer()
    await sender.add_user(user)


@user_router.callback_query(lambda callback: "Unsubscribe" in callback.data)
async def unsubscribe(callback: CallbackQuery, sender: FromDishka[ScheduleSender]):
    user: int = callback.from_user.id
    await callback.message.answer(
        text="Больше не буду слать пасту каждый день",
        reply_markup=subscribe_keyboard.as_markup(),
    )
    with suppress(TelegramAPIError):
        await callback.answer()
    await sender.remove_user(user)


@user_router.callback_query(lambda callback: "More" in callback.data)
async def more(callback: CallbackQuery, sender: FromDishka[ScheduleSender]):
    await sender.send(callback.from_user.id)
    with suppress(TelegramAPIError):
        await callback.answer()

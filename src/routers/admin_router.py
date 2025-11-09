from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka

from src.helpers import ScheduleSender

__all__ = ["configure_admin_router"]


def configure_admin_router(admin_id: int) -> Router:
    admin_router = Router(name="Admin router")
    admin_router.message.filter(F.from_user.id == admin_id)

    @admin_router.message(Command(commands=["start_mailing"]))
    async def start_mailing(message: Message, sender: FromDishka[ScheduleSender]):
        if sender.enabled:
            await message.answer(text="Рассылка уже была включена ранее")
        else:
            sender.enabled = True
            await message.answer(text="Включил рассылку")

    @admin_router.message(Command(commands=["stop_mailing"]))
    async def stop_mailing(message: Message, sender: FromDishka[ScheduleSender]):
        if sender.enabled:
            await message.answer(text="Рассылка неактивна")
        else:
            sender.enabled = False
            await message.answer(text="Выключил рассылку")

    return admin_router
import asyncio
import os
from datetime import UTC, time

import aiofiles
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.helpers.keyboards import subscribe_keyboard, unsubscribe_keyboard
from src.utils import pasta_to_markdown

from .pasta_list import PastaList

__all__ = ["ScheduleSender"]


class ScheduleSender:
    bot: Bot
    goal_time: time = time(hour=6, tzinfo=UTC)

    def __init__(
        self,
        bot: Bot,
        scheduler: AsyncIOScheduler,
        pastas_list: PastaList,
        filename: str = r"./users.txt",
    ):
        self.bot = bot
        self.users: set = set()
        self.scheduler = scheduler
        self.pastas_list: PastaList = pastas_list
        self._filename: str = filename

        self._enabled: bool = True

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    async def send_to_users(self):
        if not self.enabled:
            return
        for user_id in self.users:
            try:
                await self.bot.send_message(chat_id=user_id, text="")
                await asyncio.sleep(0.1)
            except TelegramForbiddenError:
                await self.remove_user(user_id)

    async def remove_user(self, user: int):
        """Удалить пользователя из set и из файла"""
        if user not in self.users:
            return
        self.users.remove(user)
        async with aiofiles.open(self._filename, "w") as file:
            await file.write(";".join(str(user) for user in self.users))

    async def add_user(self, user_id: int):
        """Добавить пользователя"""
        self.users.add(user_id)
        async with aiofiles.open(self._filename, "a") as file:
            await file.write(f"{user_id} ")

    def read_users(self) -> set[int]:
        if not os.path.exists(self._filename):
            return set()
        with open(self._filename) as file:
            return {int(user) for user in file.readline().split() if user and user.isdigit()}

    async def send(self, user: int):
        await self.bot.send_message(
            chat_id=user,
            text=pasta_to_markdown(await self.pastas_list.get_pasta()),
            parse_mode="MarkdownV2",
            reply_markup=unsubscribe_keyboard if user in self.users else subscribe_keyboard,
        )

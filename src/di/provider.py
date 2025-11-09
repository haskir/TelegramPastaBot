from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import Provider, Scope, make_async_container, provide

from src.helpers import PastaCache, PastaList, ScheduleSender

__all__ = ["DIProvider", "configure_dishka"]


class DIProvider(Provider):
    __slots__ = (
        "pasta_cache",
        "pasta_list",
        "sender",
    )

    def __init__(
        self,
        pasta_cache: PastaCache,
        pasta_list: PastaList,
        sender: ScheduleSender,
    ):
        self.pasta_cache: PastaCache = pasta_cache
        self.pasta_list: PastaList = pasta_list
        self.sender: ScheduleSender = sender
        super().__init__(scope=Scope.RUNTIME)

    @provide
    def provide_sender(self) -> ScheduleSender:
        return self.sender

    @provide
    def provide_pasta_list(self) -> PastaList:
        return self.pasta_list


async def initialize_services(bot: Bot, scheduler: AsyncIOScheduler) -> tuple[PastaCache, PastaList, ScheduleSender]:
    pasta_cache: PastaCache = PastaCache()
    await pasta_cache.initialize()
    pasta_list: PastaList = PastaList(pasta_cache)
    await pasta_list.initialize_list()
    sender: ScheduleSender = ScheduleSender(bot, scheduler, pasta_list)
    return pasta_cache, pasta_list, sender


async def configure_dishka(
    bot: Bot,
    dispatcher: Dispatcher,
    scheduler: AsyncIOScheduler,
) -> DIProvider:
    from dishka.integrations.aiogram import setup_dishka as setup_dishka_aiogram

    services = await initialize_services(bot, scheduler)
    provider: DIProvider = DIProvider(*services)
    container = make_async_container(provider)
    setup_dishka_aiogram(container=container, router=dispatcher, auto_inject=True)

    return provider
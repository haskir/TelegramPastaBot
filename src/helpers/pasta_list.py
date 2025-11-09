import asyncio
import os
import random
from xml.etree import ElementTree

import bs4
from httpx import AsyncClient
from loguru import logger

from .cache import PastaCache

__all__ = ["PastaList"]


def parse_pasta(text: str) -> str | None:
    try:
        soup = bs4.BeautifulSoup(text, "html.parser")
        pasta_element = soup.find("h2", string="Текст копипасты")  # noqa
        buttons_start_index = pasta_element.next_element.next_element.get_text().index("content_copy")
        return pasta_element.next_element.next_element.get_text()[0:buttons_start_index]
    except Exception as e:
        logger.error(repr(e))
        return None


class PastaList:
    copypasta_url = r"https://copypastas.ru/copypasta/"
    sitemap_url: str = "https://copypastas.ru/sitemap.xml"
    schema_path: str = ".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"

    def __init__(self, cache: PastaCache, path: str = r"./pastas.txt"):
        self.cache: PastaCache = cache
        self.path: str = path
        self.pastas: list[int] = list()

    async def initialize(self):
        if not os.path.exists(self.path):
            ids = await self.update_list_of_pastas()
            if ids:
                self.write_list_to_file(ids)
                self.pastas = ids
        else:
            self.pastas = self._read_file()

    def _read_file(self) -> list[int]:
        with open(self.path) as file:
            return [int(pasta_id) for pasta_id in file.read().split(" ") if pasta_id]

    async def _download_page(self, _id: str | int) -> str | None:
        async with AsyncClient(base_url=self.copypasta_url) as client:
            response = await client.get(f"{_id}/")
            if response.status_code != 200:
                print(response.status_code)
                return ""
            return response.text

    async def get_pasta(self) -> str | bool:
        """Get random Paste"""
        available_pastas = self.pastas
        random_id: int = random.choice(available_pastas)
        cached_pasta = await self.cache.get(random_id)
        if cached_pasta:
            return cached_pasta

        if not available_pastas:
            await self.update_list_of_pastas()
            return await self.get_pasta()

        response_text: str | None = await self._download_page(random_id)
        if not response_text:
            return "Не смог получить пасту :("
        parsed: str | None = parse_pasta(response_text)
        if not parsed:
            return await self.get_pasta()

        await self.cache.save(random_id, parsed)
        return parsed

    @classmethod
    async def update_list_of_pastas(cls) -> list[int]:
        async with AsyncClient() as client:
            res = await client.get(cls.sitemap_url)
            if res.status_code != 200:
                return list()
            root = ElementTree.fromstring(res.text)
            ids = list()
            for url in root.findall(cls.schema_path)[:-2:]:
                loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
                ID = loc.split("/")[-2]
                if ID and ID.isdigit():
                    ids.append(int(ID))
            return ids

    def write_list_to_file(self, ids: list[int]) -> None:
        with open(self.path, "w") as file:
            file.write(" ".join(str(ID) for ID in ids))

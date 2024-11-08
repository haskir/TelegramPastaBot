import asyncio
import os.path
import random

import aiofiles
import bs4
import xml.etree.ElementTree as ET
from httpx import AsyncClient


async def download_page(url: str) -> str | None:
    async with AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return ""
        return response.text


def parse_pasta(text: str) -> str:
    try:
        soup = bs4.BeautifulSoup(text, "html.parser")
        PastaElement = soup.find("h2", string="Текст копипасты")
        buttons_start_index = PastaElement.next_element.next_element.get_text().index("content_copy")
        return PastaElement.next_element.next_element.get_text()[0:buttons_start_index]
    except BaseException as e:
        print(e)
        return "Не смог запарсить пасту :("


async def get_pasta() -> str | bool:
    url = r"https://copypastas.ru/copypasta"
    available_pastas = pastas_list.pastas
    random_id: int = random.choice(available_pastas)
    cached_pasta = await cache.get(random_id)
    if cached_pasta:
        return cached_pasta
    if not available_pastas:
        await pastas_list.update_list_of_pastas()
        return await get_pasta()
    response_text = await download_page(f'{url}/{random_id}/')
    if not response_text:
        return "Не смогу получить пасту :("
    parsed = parse_pasta(response_text)
    await cache.save(random_id, parsed)
    return parsed


def add_user_to_file(user: int):
    path = r"./users.txt"
    with open(path, "a") as file:
        file.write(f'{user} ')


def read_users() -> set[int]:
    path = r"./users.txt"
    if not os.path.exists(path):
        return set()
    with open(path) as file:
        return {
            int(user) for user in file.readline().split()
            if user and user.isdigit()
        }


def remove_user(user: int):
    path = r"./users.txt"
    users = read_users()
    if user in users:
        users.remove(user)
        with open(path, "w") as file:
            file.write(";".join(str(user) for user in users))


def pasta_to_markdown(pasta: str) -> str:
    if len(pasta) < 80 and "\n" not in pasta:
        return f'`{pasta}`'
    return f'```База\n{pasta}\n```'


class PastaList:
    def __init__(self, path: str = r'./pastas.txt'):
        self.path = path
        self.pastas: list[int] = list()
        if not os.path.exists(path):
            ids = asyncio.run(self.update_list_of_pastas())
            if ids:
                self.write_list_to_file(ids)
                self.pastas = ids
        else:
            self.pastas = self._read_file()

    def _read_file(self) -> list[int]:
        with open(self.path) as file:
            return [int(pasta_id) for pasta_id in file.read().split(" ") if pasta_id]

    @staticmethod
    async def update_list_of_pastas() -> list[int]:
        url = "https://copypastas.ru/sitemap.xml"
        async with AsyncClient() as client:
            res = await client.get(url)
            if res.status_code != 200:
                return list()
            root = ET.fromstring(res.text)
            ids = list()
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')[:-2:]:
                loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
                ID = loc.split("/")[-2]
                if ID and ID.isdigit():
                    ids.append(int(ID))
            return ids

    @staticmethod
    def write_list_to_file(ids: list[int]) -> None:
        with open(r"./pastas.txt", "w") as file:
            file.write(" ".join(str(ID) for ID in ids))

    def get_random_id(self) -> int:
        return random.choice(self.pastas)


class PastaCache:
    def __init__(self, path: str = r'./pastas/'):
        self.cache: dict[int, str] = dict()
        self.path = path
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            for pasta_txt in os.listdir(path):
                with open(f'{self.path}{pasta_txt}') as file:
                    self.cache[int(pasta_txt.split(".")[0])] = file.read()

    async def get(self, ID: int) -> str:
        if ID in self.cache:
            return self.cache[ID]
        if not os.path.exists(f'{self.path}{ID}.txt'):
            return ""
        async with aiofiles.open(f'{self.path}{ID}.txt') as file:
            pasta = await file.read()
            if pasta:
                self.cache[ID] = pasta
            return pasta

    async def save(self, ID: int, pasta: str) -> None:
        self.cache[ID] = pasta
        async with aiofiles.open(f'{self.path}{ID}.txt', "w", encoding="utf-8") as file:
            await file.write(pasta)


pastas_list = PastaList()
cache = PastaCache()

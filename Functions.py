import os.path
import random
from pprint import pprint

import aiofiles
import bs4
import xml.etree.ElementTree as ET
from httpx import AsyncClient


async def update_list() -> bool:
    url = "https://copypastas.ru/sitemap.xml"
    async with AsyncClient() as client:
        res = await client.get(url)
        if res.status_code == 200:
            root = ET.fromstring(res.text)
            with open(r"./pastas.txt", "w") as file:
                for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')[:-2:]:
                    loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
                    file.write(loc.split("/")[-2] + " ")
            return True
        else:
            return False


async def read_pastas_file() -> None | list:
    path = r"./pastas.txt"
    if not os.path.exists(path):
        print("Didn't find file with pastas")
        if not await update_list():
            print("Error in read_pastas_file")
            return None
        print("Got new file")
    with open(path) as file:
        return file.readline().split(" ")


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
    available_pastas = await read_pastas_file()
    random_id: int = random.choice(available_pastas)
    cached_pasta = await cache.get(random_id)
    if cached_pasta:
        return cached_pasta
    if not available_pastas:
        await update_list()
        return await get_pasta()
    response_text = await download_page(f'{url}/{random_id}/')
    if not response_text:
        return "Не смогу получить пасту :("
    parsed = parse_pasta(response_text)
    await cache.save(random_id, parsed)
    return parsed


def add_user_to_file(user: str | int):
    path = r"./users.txt"
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write(f"{user};")
    else:
        if user in read_users():
            print("User already in Database")
            return
        with open(path, "a") as file:
            file.write(f"{user.rstrip()};")


def read_users() -> list[str]:
    path = r"./users.txt"
    if not os.path.exists(path):
        return list()
    with open(path) as file:
        return [user for user in file.readline().split(";") if user and user.isdigit()]


def remove_user(user: str | int):
    path = r"./users.txt"
    users = read_users()
    if str(user) in users:
        users.remove(str(user))
        with open(path, "w") as file:
            [file.write(user.rstrip() + ";") for user in users]


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
        async with aiofiles.open(f'{self.path}{ID}.txt', "w") as file:
            await file.write(pasta)


cache = PastaCache()

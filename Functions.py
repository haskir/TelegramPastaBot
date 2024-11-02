import os.path
import random
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


def read_pastas_file() -> None | list:
    path = r"./pastas.txt"
    if not os.path.exists(path):
        print("Didn't find file with pastas")
        if not update_list():
            print("Error in read_pastas_file")
            return None
        print("Got new file")
    with open(path) as file:
        return file.readline().split(" ")


async def get_pasta() -> str | bool:
    url = r"https://copypastas.ru/"
    available_pastas = read_pastas_file()
    if not available_pastas:
        await update_list()
        return await get_pasta()
    else:
        try:
            async with AsyncClient() as client:
                response = await client.get(f"{url}copypasta/{random.choice(available_pastas)}")
                if response.status_code != 200:
                    return "Не смогу получить пасту :("
                soup = bs4.BeautifulSoup(response.text, "html.parser")
                PastaElement = soup.find("h2", string="Текст копипасты")
                buttons_start_index = PastaElement.next_element.next_element.get_text().index("content_copy")
                return PastaElement.next_element.next_element.get_text()[0:buttons_start_index]
        except BaseException as e:
            return "Не смог запарсить пасту :("


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
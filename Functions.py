import datetime
import os.path
import random

import requests
from bs4 import BeautifulSoup


def update_list() -> bool:
    url = r"https://copypastas.ru/"
    req = requests.get(url + "ids.php")
    if req.status_code == 200:
        with open(r"./pastas.txt", "w") as file:
            file.write(req.text)
            print(f"Обновил список паст {datetime.datetime.now()}")
            return True
    print("Didn't get list of pastas")
    return False


def read_pastas_file() -> None | list:
    path = r"./pastas.txt"
    if not os.path.exists(path):
        print("Didn't find file with pastas")
        if not update_list():
            print("Error in read_pastas_file")
            return None
        print("Got new file")
    with open(path, "r") as file:
        return file.readline().split(" ")


def get_pasta() -> str | bool:
    url = r"https://copypastas.ru/"
    available_pastas = read_pastas_file()
    if not available_pastas:
        update_list()
        return get_pasta()
    else:
        pasta = requests.get(f"{url}copypasta/{random.choice(available_pastas)}")
        soup = BeautifulSoup(pasta.content, "html.parser")
        result = soup.find("div", class_="afzSy")
        [img.replace_with(img["alt"]) for img in result.find_all("img")]
        return result.get_text().strip()


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


def read_users() -> list[str] | None:
    path = r"./users.txt"
    if not os.path.exists(path):
        return None
    with open(path, "r") as file:
        return [user for user in file.readline().split(";") if user and user.isdigit()]


def remove_user(user: str | int):
    path = r"./users.txt"
    users = read_users()
    if str(user) in users:
        users.remove(str(user))
        with open(path, "w") as file:
            [file.write(user.rstrip() + ";") for user in users]


def main():
    print(get_pasta())


if __name__ == "__main__":
    main()
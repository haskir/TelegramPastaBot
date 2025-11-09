import os

import aiofiles

__all__ = ["PastaCache"]


class PastaCache:
    def __init__(self, dir_path: str = r"./pastas/"):
        self.cache: dict[int, str] = dict()
        self.dir_path: str = dir_path

    async def initialize(self):
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)
        else:
            for filename in os.listdir(self.dir_path):
                async with aiofiles.open(os.path.join(self.dir_path, filename), encoding="utf-8") as file:
                    _id: int = int(filename.split(".")[0])
                    self.cache[_id] = await file.read()

    async def get(self, ID: int) -> str:
        """Получить пасту по ID"""
        if ID in self.cache:
            return self.cache[ID]
        if not os.path.exists(f"{self.dir_path}{ID}.txt"):
            return ""
        async with aiofiles.open(f"{self.dir_path}{ID}.txt") as file:
            pasta = await file.read()
            if pasta:
                self.cache[ID] = pasta
            return pasta

    async def save(self, ID: int, pasta: str) -> None:
        """Сохранить пасту в файле"""
        self.cache[ID] = pasta
        async with aiofiles.open(
            file=f"{self.dir_path}{ID}.txt",
            mode="w",
            encoding="utf-8",
        ) as file:
            await file.write(pasta)
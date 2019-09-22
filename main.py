import os
import traceback

import asyncpg

import discord
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ghost ")

        self._ping_cache = {}
    
    def load_from_folder(self, folder):
        """Load extensions from folder"""
        for file in os.listdir(folder):
            if os.path.isdir(file) or file.startswith("_"):
                continue
                
            try:
                self.load_extension(f"{folder}.{file[:-3]}")
                print(file)
            except Exception:
                traceback.print_exc()

    async def on_connect(self):
        """On connect"""
        self.db = await asyncpg.create_pool(database="ghost", user="postgres", password=os.environ.get("PG_PASSWORD"))

        self.load_extension("jishaku")
        self.load_from_folder("cogs")

    async def on_ready(self):
        """On ready"""
        print("Connected")

if __name__ == "__main__":
    Bot().run(os.environ.get("GHOST_TOKEN") reconnect=True)

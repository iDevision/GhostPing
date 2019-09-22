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
        try:
            self.db = await asyncpg.create_pool(database="ghost", user="logan", password=os.environ.get("PG_PASSWORD"))
        except asyncpg.InvalidCatalogNameError:
            c = await asyncpg.connect(database="logan", user="logan")

            await c.execute("CREATE DATABASE ghost OWNER logan")

            self.db = await asyncpg.create_pool(database="ghost", user="logan", password=os.environ.get("PG_PASSWORD"))

        self.load_extension("jishaku")
        self.load_from_folder("cogs")

    async def on_ready(self):
        """On ready"""
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ghost help | Looking for some pings"))

        print("Connected")

if __name__ == "__main__":
    Bot().run(os.environ.get("GHOST_TOKEN"), reconnect=True)

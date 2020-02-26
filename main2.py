import os
import traceback

import asyncpg

import discord
from discord.ext import commands

import dashcord

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ghost2 ")

        self._ping_cache = {}
        
        self.remove_command("help")
        
        self.dashboard = dashcord.App(bot=self)
    
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
        self.db = await asyncpg.create_pool(database="ghost", user="postgres", password="Theboys3")
            
        self.load_extension("jishaku")
        self.load_from_folder("cogs")

    async def on_ready(self):
        """On ready"""
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="ghost help | Looking for some pings"))

        await self.dashboard.run()
        print("Connected")

bot = Bot()

@bot.dashboard.route(route="/")
async def index():
    return "test"

if __name__ == "__main__":
    bot.run("NjA2MTY3NjMwMjE0MjAxMzQ0.XjnJOQ.-VbhiSoKUaTe_loUi-JbOqvfwVk", reconnect=True)
